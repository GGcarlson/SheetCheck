"""Cell formula validation rule."""

from typing import List

from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from .base import Rule, ValidationFailure


class CellFormulaRule(Rule):
    """Rule to validate that cell formulas match expected values."""

    def run(self, workbook: Workbook) -> List[ValidationFailure]:
        """Check if cell formulas match expected values.

        Args:
            workbook: The Excel workbook to validate

        Returns:
            List of validation failures, empty if all formulas match
        """
        failures: List[ValidationFailure] = []

        # Check if this sheet has cell configurations
        if hasattr(self.sheet_config, "cells") and self.sheet_config.cells:
            # Check if the sheet exists in the workbook
            if self.sheet_name not in workbook.sheetnames:
                # Skip formula validation if sheet doesn't exist
                # (sheet existence should be handled by SheetExistsRule)
                return failures

            sheet = workbook[self.sheet_name]

            # Validate each cell configuration
            for cell_address, cell_config in self.sheet_config.cells.items():
                if isinstance(cell_config, dict) and "formula" in cell_config:
                    expected_formula = cell_config["formula"]
                    failures.extend(
                        self._validate_cell_formula(
                            sheet, cell_address, expected_formula
                        )
                    )

        return failures

    def _validate_cell_formula(
        self, sheet: Worksheet, cell_address: str, expected_formula: str
    ) -> List[ValidationFailure]:
        """Validate a specific cell's formula.

        Args:
            sheet: The worksheet object
            cell_address: Cell address (e.g., "B2")
            expected_formula: Expected formula string

        Returns:
            List of validation failures for this cell
        """
        failures: List[ValidationFailure] = []

        try:
            cell = sheet[cell_address]
            actual_value = cell.value

            # Normalize expected formula for comparison
            expected_normalized = self._normalize_formula(expected_formula)

            # Determine what we found in the cell
            if cell.data_type == "f":
                # Cell contains a formula
                # In openpyxl, formula is stored in value
                actual_formula = actual_value
                found_normalized = self._normalize_formula(actual_formula)
                found_display = actual_formula
            else:
                # Cell contains a hard-coded value
                found_normalized = ""
                if actual_value is not None:
                    found_display = str(actual_value)
                else:
                    found_display = ""

            # Compare normalized formulas
            if expected_normalized != found_normalized:
                failure = ValidationFailure(
                    type="formula_mismatch",
                    sheet=self.sheet_name,
                    cell=cell_address,
                    expected=expected_formula,
                    found=found_display,
                    fix_hint="Replace with correct formula",
                )
                failures.append(failure)

        except Exception:
            # If cell doesn't exist or other error, treat as mismatch
            failure = ValidationFailure(
                type="formula_mismatch",
                sheet=self.sheet_name,
                cell=cell_address,
                expected=expected_formula,
                found="(cell not found)",
                fix_hint="Add the expected formula to this cell",
            )
            failures.append(failure)

        return failures

    def _normalize_formula(self, formula: str) -> str:
        """Normalize formula for case-insensitive comparison and trim spaces.

        Args:
            formula: Formula string to normalize

        Returns:
            Normalized formula string
        """
        if not formula:
            return ""

        # Remove leading/trailing whitespace and convert to lowercase
        normalized = formula.strip().lower()

        # Normalize sheet reference format (Excel uses \! but YAML might use !)
        normalized = normalized.replace("\\!", "!")

        # Remove extra whitespace inside the formula
        # Split by spaces and rejoin with single spaces
        parts = normalized.split()
        normalized = " ".join(parts)

        return normalized
