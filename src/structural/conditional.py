"""Conditional formatting validation rule."""

from typing import Any, Dict, List, Optional

from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from .base import Rule, ValidationFailure


class ConditionalFormattingRule(Rule):
    """Rule to validate that expected conditional formatting rules exist."""

    def run(self, workbook: Workbook) -> List[ValidationFailure]:
        """Check if expected conditional formatting rules exist.

        Args:
            workbook: The Excel workbook to validate

        Returns:
            List of validation failures, empty if all CF rules exist and match
        """
        failures: List[ValidationFailure] = []

        # Check if this sheet has CF rule configurations
        if (
            hasattr(self.sheet_config, "expect_cf_rules")
            and self.sheet_config.expect_cf_rules
        ):
            # Check if the sheet exists in the workbook
            if self.sheet_name not in workbook.sheetnames:
                # Skip CF validation if sheet doesn't exist
                # (sheet existence should be handled by SheetExistsRule)
                return failures

            sheet = workbook[self.sheet_name]

            # Validate each expected CF rule
            for expected_cf_rule in self.sheet_config.expect_cf_rules:
                failures.extend(self._validate_cf_rule(sheet, expected_cf_rule))

        return failures

    def _validate_cf_rule(
        self, sheet: Worksheet, expected_cf_rule: Dict[str, Any]
    ) -> List[ValidationFailure]:
        """Validate a specific conditional formatting rule.

        Args:
            sheet: The worksheet object
            expected_cf_rule: Expected CF rule configuration from YAML

        Returns:
            List of validation failures for this CF rule
        """
        failures: List[ValidationFailure] = []

        expected_range = expected_cf_rule.get("range", "")
        expected_type = expected_cf_rule.get("type", "")
        expected_colors = expected_cf_rule.get("colors", [])

        # Find matching CF rule in the worksheet
        found_cf_rule = self._find_matching_cf_rule(
            sheet, expected_range, expected_type, expected_colors
        )

        if found_cf_rule is None:
            # CF rule is missing
            failure = ValidationFailure(
                type="cf_missing",
                sheet=self.sheet_name,
                range=expected_range,
                expected={"type": expected_type, "colors": expected_colors},
                found=None,
                fix_hint=(
                    f"Add {self._get_cf_description(expected_type, expected_colors)} "
                    f"CF to {expected_range}"
                ),
            )
            failures.append(failure)

        return failures

    def _find_matching_cf_rule(
        self,
        sheet: Worksheet,
        expected_range: str,
        expected_type: str,
        expected_colors: List[str],
    ) -> Optional[Dict[str, Any]]:
        """Find a conditional formatting rule that matches the expected criteria.

        Args:
            sheet: The worksheet object
            expected_range: Expected range (e.g., "C2:C50")
            expected_type: Expected rule type (e.g., "colorScale")
            expected_colors: Expected colors list

        Returns:
            Dict describing the found rule, or None if not found
        """
        # Normalize expected colors
        normalized_expected_colors = [
            self._normalize_color(color) for color in expected_colors
        ]

        # Iterate through all conditional formatting sets
        for cf_set in sheet.conditional_formatting:
            # Check if range matches
            if cf_set.sqref != expected_range:
                continue

            # Check each rule in this CF set
            for rule in cf_set.cfRule:
                if rule.type == expected_type:
                    if expected_type == "colorScale" and rule.colorScale:
                        # Extract colors from the color scale
                        found_colors = []
                        for color in rule.colorScale.color:
                            if color.rgb:
                                found_colors.append(self._normalize_color(color.rgb))

                        # Compare colors
                        if found_colors == normalized_expected_colors:
                            return {
                                "type": rule.type,
                                "colors": [
                                    self._denormalize_color(color)
                                    for color in found_colors
                                ],
                                "range": cf_set.sqref,
                            }

        return None

    def _normalize_color(self, color: str) -> str:
        """Normalize color to consistent format for comparison.

        Args:
            color: Color string (hex with or without # or ARGB prefix)

        Returns:
            Normalized color string (uppercase hex without prefixes)
        """
        # Remove # if present
        if color.startswith("#"):
            color = color[1:]

        # Remove ARGB prefix (00) if present (Excel adds this)
        if len(color) == 8 and color.startswith("00"):
            color = color[2:]

        # Convert to uppercase for consistent comparison
        return color.upper()

    def _denormalize_color(self, color: str) -> str:
        """Convert normalized color back to standard hex format.

        Args:
            color: Normalized color string

        Returns:
            Standard hex color with # prefix
        """
        return f"#{color}"

    def _get_cf_description(self, cf_type: str, colors: List[str]) -> str:
        """Get human-readable description of CF rule.

        Args:
            cf_type: Conditional formatting rule type
            colors: List of colors

        Returns:
            Human-readable description
        """
        if cf_type == "colorScale":
            color_count = len(colors)
            return f"{color_count}-color scale"
        return cf_type
