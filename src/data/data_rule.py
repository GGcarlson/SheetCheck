"""Data validation rule wrapper for Great Expectations integration."""

import tempfile
from pathlib import Path
from typing import Any, List

from openpyxl import Workbook

from ..structural.base import Rule, ValidationFailure
from .ge_adapter import run_expectations, is_ge_supported


class DataValidationRule(Rule):
    """Rule wrapper for Great Expectations data validation.

    This class adapts the Great Expectations validation system to work
    with the existing structural validation framework by implementing
    the Rule interface.
    """

    def __init__(self, rule_file_path: str, sheet_config: Any) -> None:
        """Initialize data validation rule.

        Args:
            rule_file_path: Path to the YAML file containing GE expectations
            sheet_config: Configuration object (not used for data validation)
        """
        super().__init__("", sheet_config)  # Sheet name determined from rule file
        self.rule_file_path = Path(rule_file_path)

    def run(self, workbook: Workbook) -> List[ValidationFailure]:
        """Execute Great Expectations validation against workbook data.

        Args:
            workbook: The Excel workbook to validate

        Returns:
            List of ValidationFailure objects representing GE validation failures
        """
        failures = []

        # Check if Great Expectations is available
        if not is_ge_supported():
            failures.append(
                ValidationFailure(
                    type="dependency_error",
                    message=(
                        "pandas and great-expectations are required "
                        "for data validation"
                    ),
                    fix_hint=(
                        "Install dependencies: "
                        "pip install pandas great-expectations"
                    ),
                )
            )
            return failures

        try:
            # Save workbook to temporary file for GE processing
            with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp_file:
                temp_path = Path(tmp_file.name)
                workbook.save(temp_path)

            try:
                # Run Great Expectations validation
                validation_result = run_expectations(temp_path, self.rule_file_path)

                # Convert GE failures to ValidationFailure objects
                if not validation_result.success:
                    ge_failures = validation_result.get_failures()
                    for ge_failure in ge_failures:
                        failure = self._convert_ge_failure_to_validation_failure(
                            ge_failure
                        )
                        failures.append(failure)

            finally:
                # Clean up temporary file
                try:
                    temp_path.unlink()
                except OSError:
                    pass

        except Exception as e:
            failures.append(
                ValidationFailure(
                    type="data_validation_error",
                    message=f"Data validation failed: {e}",
                    fix_hint="Check data file format and rule configuration",
                )
            )

        return failures

    def _convert_ge_failure_to_validation_failure(
        self, ge_failure: dict
    ) -> ValidationFailure:
        """Convert a Great Expectations failure to a ValidationFailure object.

        Args:
            ge_failure: Dictionary containing GE validation failure details

        Returns:
            ValidationFailure object in expected format for JSON output
        """
        expectation_config = ge_failure.get("expectation_config", {})
        expectation_type = expectation_config.get("expectation_type", "unknown")
        kwargs = expectation_config.get("kwargs", {})
        column = kwargs.get("column", "unknown")

        result = ge_failure.get("result", {})
        observed_value = result.get("observed_value")
        unexpected_count = result.get("unexpected_count", 0)

        # Determine sheet name from rule file or use default
        sheet_name = "Data"  # Default, could be extracted from rule config
        try:
            import yaml

            with open(self.rule_file_path, "r") as f:
                rule_config = yaml.safe_load(f)
                target_config = rule_config.get("target", {})
                sheet_name = target_config.get("sheet", "Data")
        except Exception:
            pass  # Use default sheet name if can't read rule file

        # Create ValidationFailure with proper fields for JSON output
        failure = ValidationFailure(
            type="expectation_failed",
            sheet=sheet_name,
            message=f"{expectation_type} failed on column '{column}'",
            expected=expectation_type,
            found=f"unexpected_count: {unexpected_count}",
        )

        # Add custom fields as attributes for JSON serialization
        setattr(failure, "expectation", expectation_type)
        setattr(failure, "column", column)
        setattr(failure, "unexpected_count", unexpected_count)
        if observed_value:
            setattr(failure, "observed_value", str(observed_value))

        return failure

    def to_dict(self) -> dict:
        """Convert rule to dictionary representation.

        Returns:
            Dictionary containing rule information
        """
        return {
            "type": "data_validation",
            "rule_file": str(self.rule_file_path),
        }
