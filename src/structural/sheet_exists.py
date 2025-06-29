"""Sheet existence validation rule."""

from typing import List

from openpyxl import Workbook

from .base import Rule, ValidationFailure


class SheetExistsRule(Rule):
    """Rule to validate that required sheets exist in the workbook."""

    def run(self, workbook: Workbook) -> List[ValidationFailure]:
        """Check if the required sheet exists in the workbook.

        Args:
            workbook: The Excel workbook to validate

        Returns:
            List of validation failures, empty if sheet exists
        """
        failures = []

        # Check if this sheet is required to exist
        if hasattr(self.sheet_config, "must_exist") and self.sheet_config.must_exist:
            # Get all sheet names in the workbook
            sheet_names = workbook.sheetnames

            # Check if our required sheet exists
            if self.sheet_name not in sheet_names:
                failure = ValidationFailure(
                    type="sheet_missing",
                    sheet=self.sheet_name,
                    fix_hint=f"Add a sheet named '{self.sheet_name}'",
                )
                failures.append(failure)

        return failures
