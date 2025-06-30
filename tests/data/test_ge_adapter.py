"""Tests for Great Expectations adapter functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

try:
    import pandas as pd
except ImportError:
    pd = None

try:
    import great_expectations as ge
except ImportError:
    ge = None

from src.data.ge_adapter import (
    ValidationResult,
    run_expectations,
    is_ge_supported,
    create_sample_rule_yaml,
)


class TestValidationResult:
    """Test cases for ValidationResult class."""

    def test_validation_result_creation(self):
        """Test creating ValidationResult with basic data."""
        results = [
            {"success": True, "expectation_config": {"expectation_type": "test1"}},
            {"success": False, "expectation_config": {"expectation_type": "test2"}},
        ]
        statistics = {"successful_expectations": 1, "evaluated_expectations": 2}

        result = ValidationResult(success=False, results=results, statistics=statistics)

        assert result.success is False
        assert len(result.results) == 2
        assert result.statistics == statistics
        assert "FAILED" in str(result)

    def test_get_failures(self):
        """Test extracting failed validations."""
        results = [
            {"success": True, "expectation_config": {"expectation_type": "test1"}},
            {"success": False, "expectation_config": {"expectation_type": "test2"}},
            {"success": False, "expectation_config": {"expectation_type": "test3"}},
        ]

        result = ValidationResult(success=False, results=results, statistics={})

        failures = result.get_failures()
        assert len(failures) == 2
        assert all(not f["success"] for f in failures)

    def test_get_failure_summary_with_failures(self):
        """Test failure summary generation."""
        results = [
            {
                "success": False,
                "expectation_config": {
                    "expectation_type": "expect_column_values_to_not_be_null",
                    "kwargs": {"column": "id"},
                },
                "result": {"observed_value": "null_count: 2"},
            }
        ]

        result = ValidationResult(success=False, results=results, statistics={})
        summary = result.get_failure_summary()

        assert "1 validation failures" in summary
        assert "expect_column_values_to_not_be_null" in summary
        assert "column 'id'" in summary

    def test_get_failure_summary_no_failures(self):
        """Test failure summary when all validations pass."""
        results = [
            {"success": True, "expectation_config": {"expectation_type": "test1"}}
        ]

        result = ValidationResult(success=True, results=results, statistics={})
        summary = result.get_failure_summary()

        assert summary == "All validations passed!"


@pytest.mark.skipif(
    pd is None or ge is None, reason="pandas or great-expectations not available"
)
class TestRunExpectations:
    """Test cases for run_expectations function."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = Path(tempfile.mkdtemp())

        # Use existing test fixtures
        self.excel_path = Path(__file__).parent.parent / "fixtures" / "data_sample.xlsx"
        self.rule_path = (
            Path(__file__).parent.parent / "fixtures" / "rule_data_non_null.yaml"
        )

    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_non_null_pass(self):
        """Test successful validation with non-null data."""
        # This should pass since our test data has no null values
        result = run_expectations(self.excel_path, self.rule_path)

        assert isinstance(result, ValidationResult)
        assert result.success is True
        assert len(result.results) > 0
        assert result.statistics["successful_expectations"] > 0
        assert result.rule_path == str(self.rule_path)

    def test_file_not_found_errors(self):
        """Test proper error handling for missing files."""
        missing_excel = self.temp_dir / "missing.xlsx"
        missing_rule = self.temp_dir / "missing.yaml"

        with pytest.raises(FileNotFoundError, match="Excel file not found"):
            run_expectations(missing_excel, self.rule_path)

        with pytest.raises(FileNotFoundError, match="Rule file not found"):
            run_expectations(self.excel_path, missing_rule)

    def test_invalid_rule_structure(self):
        """Test error handling for invalid YAML rule structure."""
        invalid_rule_path = self.temp_dir / "invalid_rule.yaml"

        # Create invalid rule file (valid YAML but invalid rule structure)
        with open(invalid_rule_path, "w") as f:
            f.write("invalid_rule_structure: true\nmissing_rule_type: data")

        with pytest.raises(ValueError):
            run_expectations(self.excel_path, invalid_rule_path)

    def test_wrong_rule_type(self):
        """Test error handling for wrong rule type."""
        wrong_rule_path = self.temp_dir / "wrong_rule.yaml"

        with open(wrong_rule_path, "w") as f:
            f.write("rule_type: structural_validation\nexpectations: []")

        with pytest.raises(ValueError, match="Expected rule_type 'data_validation'"):
            run_expectations(self.excel_path, wrong_rule_path)

    def test_empty_expectations(self):
        """Test error handling for rules with no expectations."""
        empty_rule_path = self.temp_dir / "empty_rule.yaml"

        with open(empty_rule_path, "w") as f:
            f.write("rule_type: data_validation\nexpectations: []")

        with pytest.raises(ValueError, match="must contain 'expectations' list"):
            run_expectations(self.excel_path, empty_rule_path)

    def test_string_and_path_objects(self):
        """Test that both string and Path objects work as input."""
        # Test with string paths
        result_str = run_expectations(str(self.excel_path), str(self.rule_path))

        # Test with Path objects
        result_path = run_expectations(self.excel_path, self.rule_path)

        # Both should succeed
        assert result_str.success is True
        assert result_path.success is True

    def test_excel_with_data_containing_nulls(self):
        """Test validation failure when data contains null values."""
        # Create Excel file with null values
        null_excel_path = self.temp_dir / "null_data.xlsx"

        # Create DataFrame with null values
        df_with_nulls = pd.DataFrame(
            {
                "id": [1, 2, None, 4],  # Has null value
                "date": ["2024-01-01", "2024-01-02", "2024-01-03", None],  # Has null
                "amount": [100.0, 200.0, 300.0, 400.0],  # No nulls
            }
        )

        df_with_nulls.to_excel(null_excel_path, sheet_name="Data", index=False)

        # Run validation - should fail due to null values
        result = run_expectations(null_excel_path, self.rule_path)

        assert isinstance(result, ValidationResult)
        # May pass or fail depending on success threshold, but should have some failures
        failures = result.get_failures()
        assert len(failures) > 0

        # Check failure summary contains information about null values
        summary = result.get_failure_summary()
        assert "validation failures" in summary

    def test_nonexistent_sheet(self):
        """Test error handling for nonexistent sheet name."""
        # Create rule targeting nonexistent sheet
        bad_sheet_rule_path = self.temp_dir / "bad_sheet_rule.yaml"

        with open(bad_sheet_rule_path, "w") as f:
            f.write(
                """
rule_type: data_validation
target:
  sheet: NonexistentSheet
expectations:
  - expectation_type: expect_column_values_to_not_be_null
    kwargs:
      column: id
"""
            )

        with pytest.raises((ValueError, RuntimeError)):
            run_expectations(self.excel_path, bad_sheet_rule_path)

    def test_success_threshold_application(self):
        """Test that success threshold is properly applied."""
        # Create rule with high success threshold
        threshold_rule_path = self.temp_dir / "threshold_rule.yaml"

        with open(threshold_rule_path, "w") as f:
            f.write(
                """
rule_type: data_validation
target:
  sheet: Data
expectations:
  - expectation_type: expect_column_values_to_not_be_null
    kwargs:
      column: id
validation:
  success_threshold: 1.0  # 100% must pass
  catch_exceptions: true
"""
            )

        result = run_expectations(self.excel_path, threshold_rule_path)
        assert isinstance(result, ValidationResult)
        # Should still pass since our test data is clean


@pytest.mark.skipif(
    pd is None or ge is None, reason="pandas or great-expectations not available"
)
class TestIsGeSupported:
    """Test cases for Great Expectations support detection."""

    def test_is_ge_supported_with_dependencies(self):
        """Test support detection when dependencies are available."""
        assert is_ge_supported() is True

    @patch("src.data.ge_adapter.pd", None)
    def test_is_ge_supported_without_pandas(self):
        """Test support detection when pandas is not available."""
        assert is_ge_supported() is False

    @patch("src.data.ge_adapter.ge", None)
    def test_is_ge_supported_without_ge(self):
        """Test support detection when great-expectations is not available."""
        assert is_ge_supported() is False


class TestCreateSampleRuleYaml:
    """Test cases for sample rule generation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_create_sample_rule_yaml(self):
        """Test creation of sample rule YAML file."""
        output_path = self.temp_dir / "sample_rule.yaml"

        create_sample_rule_yaml(output_path)

        assert output_path.exists()

        # Verify content structure
        import yaml

        with open(output_path) as f:
            rule_data = yaml.safe_load(f)

        assert rule_data["rule_type"] == "data_validation"
        assert "expectations" in rule_data
        assert len(rule_data["expectations"]) > 0
        assert "validation" in rule_data

    def test_create_sample_rule_yaml_with_nested_directory(self):
        """Test creation with nested directory path."""
        output_path = self.temp_dir / "subdir" / "nested" / "sample_rule.yaml"

        create_sample_rule_yaml(output_path)

        assert output_path.exists()
        assert output_path.parent.exists()


class TestDependencyHandling:
    """Test cases for dependency import handling."""

    @patch("src.data.ge_adapter.pd", None)
    def test_run_expectations_without_pandas(self):
        """Test error handling when pandas is not available."""
        with pytest.raises(ImportError, match="pandas is required"):
            run_expectations("dummy.xlsx", "dummy.yaml")

    @patch("src.data.ge_adapter.ge", None)
    def test_run_expectations_without_ge(self):
        """Test error handling when great-expectations is not available."""
        with pytest.raises(ImportError, match="great-expectations is required"):
            run_expectations("dummy.xlsx", "dummy.yaml")


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    @pytest.mark.skipif(pd is None, reason="pandas not available")
    def test_empty_excel_file(self):
        """Test handling of empty Excel file."""
        empty_excel_path = self.temp_dir / "empty.xlsx"

        # Create empty Excel file
        df_empty = pd.DataFrame()
        df_empty.to_excel(empty_excel_path, sheet_name="Data", index=False)

        rule_path = self.temp_dir / "test_rule.yaml"
        with open(rule_path, "w") as f:
            f.write(
                """
rule_type: data_validation
target:
  sheet: Data
expectations:
  - expectation_type: expect_column_values_to_not_be_null
    kwargs:
      column: id
"""
            )

        with pytest.raises(ValueError, match="contains no data"):
            run_expectations(empty_excel_path, rule_path)

    def test_malformed_yaml_file(self):
        """Test handling of malformed YAML file."""
        bad_yaml_path = self.temp_dir / "bad.yaml"

        with open(bad_yaml_path, "w") as f:
            f.write("invalid: yaml: [unclosed")

        import yaml

        with pytest.raises((yaml.YAMLError, ValueError, RuntimeError)):
            run_expectations("tests/fixtures/data_sample.xlsx", bad_yaml_path)
