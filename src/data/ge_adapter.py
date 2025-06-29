"""Great Expectations adapter for data validation in Excel files."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

try:
    import pandas as pd
except ImportError:
    pd = None  # type: ignore

try:
    import great_expectations as ge
except ImportError:
    ge = None  # type: ignore


logger = logging.getLogger(__name__)


class ValidationResult:
    """Container for Great Expectations validation results."""

    def __init__(
        self,
        success: bool,
        results: List[Dict[str, Any]],
        statistics: Dict[str, Any],
        rule_path: Optional[str] = None,
    ):
        self.success = success
        self.results = results
        self.statistics = statistics
        self.rule_path = rule_path

    def __str__(self) -> str:
        """String representation showing validation summary."""
        status = "PASSED" if self.success else "FAILED"
        return f"ValidationResult(status={status}, checks={len(self.results)})"

    def get_failures(self) -> List[Dict[str, Any]]:
        """Get list of failed validation results."""
        return [result for result in self.results if not result.get("success", False)]

    def get_failure_summary(self) -> str:
        """Get human-readable summary of validation failures."""
        failures = self.get_failures()
        if not failures:
            return "All validations passed!"

        summary_lines = [f"Found {len(failures)} validation failures:"]
        for i, failure in enumerate(failures, 1):
            expectation = failure.get("expectation_config", {})
            expectation_type = expectation.get("expectation_type", "unknown")
            kwargs = expectation.get("kwargs", {})
            column = kwargs.get("column", "unknown")

            result = failure.get("result", {})
            observed_value = result.get("observed_value")

            summary_lines.append(
                f"  {i}. {expectation_type} on column '{column}' - "
                f"observed: {observed_value}"
            )

        return "\n".join(summary_lines)


def run_expectations(
    xlsx_path: Union[str, Path], rule_yaml_path: Union[str, Path]
) -> ValidationResult:
    """Run Great Expectations validations on Excel data.

    Loads Excel file into pandas DataFrame, creates Great Expectations dataset,
    and runs validations defined in YAML rule file.

    Args:
        xlsx_path: Path to Excel file to validate
        rule_yaml_path: Path to YAML file containing GE expectations

    Returns:
        ValidationResult with success status and detailed results

    Raises:
        ImportError: If pandas or great-expectations not available
        FileNotFoundError: If Excel or YAML files don't exist
        ValueError: If invalid rule format or Excel structure
        RuntimeError: If validation execution fails

    Example:
        >>> result = run_expectations("data.xlsx", "rules.yaml")
        >>> if not result.success:
        ...     print(result.get_failure_summary())
    """
    # Validate dependencies
    if pd is None:
        raise ImportError("pandas is required for Excel data validation")
    if ge is None:
        raise ImportError("great-expectations is required for data validation")

    # Convert paths to Path objects
    xlsx_path = Path(xlsx_path)
    rule_yaml_path = Path(rule_yaml_path)

    # Validate input files exist
    if not xlsx_path.exists():
        raise FileNotFoundError(f"Excel file not found: {xlsx_path}")
    if not rule_yaml_path.exists():
        raise FileNotFoundError(f"Rule file not found: {rule_yaml_path}")

    try:
        # Load and parse rule configuration
        with open(rule_yaml_path, "r", encoding="utf-8") as f:
            rule_config = yaml.safe_load(f)

        # Validate rule structure
        if not isinstance(rule_config, dict):
            raise ValueError("Rule file must contain a YAML dictionary")

        rule_type = rule_config.get("rule_type")
        if rule_type != "data_validation":
            raise ValueError(f"Expected rule_type 'data_validation', got '{rule_type}'")

        expectations_config = rule_config.get("expectations", [])
        if not expectations_config:
            raise ValueError("Rule file must contain 'expectations' list")

        target_config = rule_config.get("target", {})
        sheet_name = target_config.get("sheet", 0)  # Default to first sheet

        # Load Excel data into pandas DataFrame
        logger.info(f"Loading Excel file: {xlsx_path}, sheet: {sheet_name}")
        df = pd.read_excel(xlsx_path, sheet_name=sheet_name)

        if df.empty:
            raise ValueError(f"Excel sheet '{sheet_name}' contains no data")

        logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")

        # Convert DataFrame to Great Expectations dataset
        ge_df = ge.from_pandas(df)

        # Add expectations from rule configuration
        for expectation_config in expectations_config:
            expectation_type = expectation_config.get("expectation_type")
            kwargs = expectation_config.get("kwargs", {})
            meta = expectation_config.get("meta", {})

            if not expectation_type:
                logger.warning("Skipping expectation without type")
                continue

            # Add expectation to dataset
            try:
                getattr(ge_df, expectation_type)(**kwargs, meta=meta)
                logger.debug(f"Added expectation: {expectation_type}")
            except AttributeError:
                logger.error(f"Unknown expectation type: {expectation_type}")
                continue
            except Exception as e:
                logger.error(f"Failed to add expectation {expectation_type}: {e}")
                continue

        # Run validation
        logger.info(f"Running {len(expectations_config)} expectations")
        validation_result = ge_df.validate(catch_exceptions=True)

        # Process results
        success = validation_result.success
        results = validation_result.results
        statistics = validation_result.statistics

        # Apply success threshold if specified
        validation_config = rule_config.get("validation", {})
        success_threshold = validation_config.get("success_threshold")

        if success_threshold is not None:
            success_rate = statistics.get("successful_expectations", 0) / max(
                statistics.get("evaluated_expectations", 1), 1
            )
            if success_rate < success_threshold:
                success = False
                logger.warning(
                    f"Success rate {success_rate:.2%} below threshold "
                    f"{success_threshold:.2%}"
                )

        logger.info(
            f"Validation completed: {statistics.get('successful_expectations', 0)}/"
            f"{statistics.get('evaluated_expectations', 0)} passed"
        )

        return ValidationResult(
            success=success,
            results=results,
            statistics=statistics,
            rule_path=str(rule_yaml_path),
        )

    except Exception as e:
        if isinstance(e, (ImportError, FileNotFoundError, ValueError)):
            raise
        else:
            raise RuntimeError(f"Great Expectations validation failed: {e}") from e


def is_ge_supported() -> bool:
    """Check if Great Expectations functionality is supported.

    Returns:
        True if pandas and great-expectations are available, False otherwise
    """
    return pd is not None and ge is not None


def create_sample_rule_yaml(output_path: Union[str, Path]) -> None:
    """Create a sample Great Expectations rule YAML file.

    Args:
        output_path: Path where to save the sample rule file

    Example:
        >>> create_sample_rule_yaml("sample_data_rules.yaml")
    """
    sample_rule = {
        "rule_type": "data_validation",
        "description": "Sample data validation rules",
        "target": {"sheet": "Data"},
        "expectations": [
            {
                "expectation_type": "expect_column_values_to_not_be_null",
                "kwargs": {"column": "id"},
                "meta": {"notes": "ID column must not be null"},
            },
            {
                "expectation_type": "expect_column_values_to_be_of_type",
                "kwargs": {"column": "amount", "type_": "float"},
                "meta": {"notes": "Amount should be numeric"},
            },
            {
                "expectation_type": "expect_column_values_to_be_between",
                "kwargs": {"column": "amount", "min_value": 0},
                "meta": {"notes": "Amount should be positive"},
            },
        ],
        "validation": {"success_threshold": 0.95, "catch_exceptions": True},
    }

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(sample_rule, f, default_flow_style=False, indent=2)

    logger.info(f"Created sample rule file: {output_path}")
