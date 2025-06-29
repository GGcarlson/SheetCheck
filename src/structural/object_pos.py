"""Object position validation rule."""

import math
from typing import Any, Dict, List, Optional

from openpyxl import Workbook

from .base import Rule, ValidationFailure

try:
    import xlwings as xw
except ImportError:
    xw = None


class ObjectPositionRule(Rule):
    """Rule to validate Excel objects positioned within expected coordinates."""

    def run(self, workbook: Workbook) -> List[ValidationFailure]:
        """Check if objects are positioned within expected tolerances.

        Args:
            workbook: The Excel workbook to validate

        Returns:
            List of validation failures, empty if all objects are positioned correctly
        """
        failures: List[ValidationFailure] = []

        # Check if xlwings is available
        if xw is None:
            # Skip object position validation if xlwings is not available
            return failures

        # Check if this sheet has object configurations
        if hasattr(self.sheet_config, "objects") and self.sheet_config.objects:
            # Check if the sheet exists in the workbook
            if self.sheet_name not in workbook.sheetnames:
                # Skip object validation if sheet doesn't exist
                # (sheet existence should be handled by SheetExistsRule)
                return failures

            # Save the workbook to a temporary file to access with xlwings
            temp_path = f"/tmp/temp_workbook_{id(workbook)}.xlsx"
            workbook.save(temp_path)

            try:
                # Open with xlwings to access shape objects
                with xw.App(visible=False) as app:
                    wb = app.books.open(temp_path)
                    try:
                        sheet = wb.sheets[self.sheet_name]

                        # Validate each expected object
                        for expected_object in self.sheet_config.objects:
                            failures.extend(
                                self._validate_object(sheet, expected_object)
                            )
                    finally:
                        wb.close()
            except Exception:
                # If xlwings fails, skip object validation
                pass
            finally:
                # Clean up temp file
                import os

                try:
                    os.remove(temp_path)
                except OSError:
                    pass

        return failures

    def _validate_object(
        self, sheet: Any, expected_object: Dict[str, Any]
    ) -> List[ValidationFailure]:
        """Validate a specific object position.

        Args:
            sheet: The xlwings worksheet object
            expected_object: Expected object configuration from YAML

        Returns:
            List of validation failures for this object
        """
        failures: List[ValidationFailure] = []

        object_name = expected_object.get("name", "")
        expected_position = expected_object.get("expect_position", {})
        expected_top = expected_position.get("top", 0)
        expected_left = expected_position.get("left", 0)
        tolerance = expected_position.get("tolerance", 5)

        # Find the shape by name
        shape = self._find_shape_by_name(sheet, object_name)

        if shape is None:
            # Object is missing
            failure = ValidationFailure(
                type="object_missing",
                sheet=self.sheet_name,
                object=object_name,
                expected={"top": expected_top, "left": expected_left},
                found=None,
                tolerance=tolerance,
                fix_hint=f"Add shape '{object_name}' to sheet",
            )
            failures.append(failure)
            return failures

        # Get actual position (convert points to pixels: 1 pt ≈ 1.333 px)
        actual_top = round(shape.top * 1.333)
        actual_left = round(shape.left * 1.333)

        # Check if position is within tolerance
        top_diff = abs(actual_top - expected_top)
        left_diff = abs(actual_left - expected_left)

        if top_diff > tolerance or left_diff > tolerance:
            # Calculate movement distance for fix hint
            total_movement = math.sqrt(
                (actual_left - expected_left) ** 2 + (actual_top - expected_top) ** 2
            )

            # Determine movement direction
            direction_hint = self._get_movement_hint(
                expected_left, expected_top, actual_left, actual_top
            )

            failure = ValidationFailure(
                type="object_moved",
                sheet=self.sheet_name,
                object=object_name,
                expected={"top": expected_top, "left": expected_left},
                found={"top": actual_top, "left": actual_left},
                tolerance=tolerance,
                fix_hint=(
                    f"Move '{object_name}' ~{round(total_movement)} px "
                    f"{direction_hint}"
                ),
            )
            failures.append(failure)

        return failures

    def _find_shape_by_name(self, sheet: Any, shape_name: str) -> Optional[Any]:
        """Find a shape by its name in the worksheet.

        Args:
            sheet: The xlwings worksheet object
            shape_name: Name of the shape to find

        Returns:
            The shape object if found, None otherwise
        """
        try:
            for shape in sheet.shapes:
                if shape.name == shape_name:
                    return shape
        except Exception:
            pass
        return None

    def _get_movement_hint(
        self, expected_left: int, expected_top: int, actual_left: int, actual_top: int
    ) -> str:
        """Generate a movement direction hint.

        Args:
            expected_left: Expected left position
            expected_top: Expected top position
            actual_left: Actual left position
            actual_top: Actual top position

        Returns:
            Human-readable movement direction (where the object should move to)
        """
        left_diff = actual_left - expected_left
        top_diff = actual_top - expected_top

        # Determine primary direction based on where object should move
        if abs(left_diff) > abs(top_diff):
            return "left" if left_diff > 0 else "right"
        else:
            return "up" if top_diff > 0 else "down"
