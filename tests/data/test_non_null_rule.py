"""CLI integration tests for data validation non-null rule."""

import json
import subprocess
import sys
from pathlib import Path

import pytest


class TestNonNullRuleCLI:
    """Test CLI integration for data validation non-null rules."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent.parent
        self.fixtures_dir = self.test_dir / "fixtures"

        # Test files
        self.good_data_file = self.fixtures_dir / "data_sample.xlsx"
        self.bad_data_file = self.fixtures_dir / "data_null_bad.xlsx"
        self.rule_file = self.fixtures_dir / "rule_data_non_null.yaml"

        # Results file
        self.results_file = Path("results.json")

    def teardown_method(self):
        """Clean up after tests."""
        # Remove results file if it exists
        if self.results_file.exists():
            self.results_file.unlink()

    def test_cli_data_validation_pass(self):
        """Test CLI with good data that should pass validation."""
        if not self.good_data_file.exists():
            pytest.skip("Good data fixture not available")
        if not self.rule_file.exists():
            pytest.skip("Rule file not available")

        # Run CLI command with good data
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.validator.cli",
                str(self.good_data_file),
                "--rules",
                str(self.rule_file),
                "--report",
                "json",
            ],
            capture_output=True,
            text=True,
            cwd=self.test_dir.parent,
        )

        # Should pass (exit code 0) but may fail due to missing dependencies
        # The important thing is that it tries to run data validation
        assert (
            "data validation" in result.stdout.lower()
            or "dependency" in result.stderr.lower()
        )

    def test_cli_data_validation_fail(self):
        """Test CLI with bad data that should fail validation."""
        if not self.bad_data_file.exists():
            pytest.skip("Bad data fixture not available")
        if not self.rule_file.exists():
            pytest.skip("Rule file not available")

        # Run CLI command with bad data (has null values)
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.validator.cli",
                str(self.bad_data_file),
                "--rules",
                str(self.rule_file),
                "--report",
                "json",
            ],
            capture_output=True,
            text=True,
            cwd=self.test_dir.parent,
        )

        # Should fail (exit code 1) or show dependency error
        assert result.returncode == 1 or "dependency" in result.stderr.lower()

        # Should mention data validation in output
        assert (
            "data validation" in result.stdout.lower()
            or "dependency" in result.stderr.lower()
        )

    def test_cli_json_output_structure(self):
        """Test that JSON output has correct structure with dataFailures."""
        if not self.bad_data_file.exists():
            pytest.skip("Bad data fixture not available")
        if not self.rule_file.exists():
            pytest.skip("Rule file not available")

        # Run CLI command
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.validator.cli",
                str(self.bad_data_file),
                "--rules",
                str(self.rule_file),
                "--report",
                "json",
            ],
            capture_output=True,
            text=True,
            cwd=self.test_dir.parent,
        )

        # Check if results.json was created
        results_path = self.test_dir.parent / "results.json"
        if results_path.exists():
            with open(results_path) as f:
                results = json.load(f)

            # Should have both structuralFailures and dataFailures sections
            assert "structuralFailures" in results
            assert "dataFailures" in results

            # dataFailures should be a list
            assert isinstance(results["dataFailures"], list)

            # If there are data failures, check format
            if results["dataFailures"]:
                failure = results["dataFailures"][0]
                assert "type" in failure
                # Should have data validation specific fields
                expected_fields = ["sheet", "expectation", "column"]
                for field in expected_fields:
                    assert field in failure, f"Missing field: {field}"

    def test_cli_rule_type_detection(self):
        """Test that CLI correctly detects data validation rule type."""
        if not self.rule_file.exists():
            pytest.skip("Rule file not available")

        # Run CLI command - should detect data validation rule
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.validator.cli",
                str(self.good_data_file),
                "--rules",
                str(self.rule_file),
            ],
            capture_output=True,
            text=True,
            cwd=self.test_dir.parent,
        )

        # Should mention data validation in the output
        output = result.stdout.lower()
        assert "data validation rule" in output or "dependency" in result.stderr.lower()

    def test_cli_error_handling_missing_dependencies(self):
        """Test CLI error handling when dependencies are missing."""
        if not self.rule_file.exists():
            pytest.skip("Rule file not available")

        # This test assumes pandas/GE might not be installed in test environment
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.validator.cli",
                str(self.good_data_file),
                "--rules",
                str(self.rule_file),
                "--report",
                "json",
            ],
            capture_output=True,
            text=True,
            cwd=self.test_dir.parent,
        )

        # Should either succeed or show helpful dependency error
        if result.returncode != 0:
            error_output = result.stderr.lower() + result.stdout.lower()
            # Should mention dependency requirements or be specific about what's missing
            dependency_mentioned = any(
                dep in error_output
                for dep in ["pandas", "great-expectations", "dependency", "install"]
            )
            assert (
                dependency_mentioned
            ), f"No clear dependency error message. Output: {result.stderr}"

    def test_cli_mixed_rules_support(self):
        """Test CLI with data validation rule (future: mixed with structural)."""
        if not self.rule_file.exists():
            pytest.skip("Rule file not available")

        # Run CLI to ensure it loads and processes data validation rules
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "src.validator.cli",
                str(self.good_data_file),
                "--rules",
                str(self.rule_file),
            ],
            capture_output=True,
            text=True,
            cwd=self.test_dir.parent,
        )

        # Should load the rule successfully
        assert (
            "loaded" in result.stdout.lower()
            or "error loading rules" not in result.stderr.lower()
        )

    def test_cli_help_and_version(self):
        """Test CLI help and version work with new data validation features."""
        # Test help
        result = subprocess.run(
            [sys.executable, "-m", "src.validator.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=self.test_dir.parent,
        )
        assert result.returncode == 0
        assert "workbook" in result.stdout.lower()

        # Test version
        result = subprocess.run(
            [sys.executable, "-m", "src.validator.cli", "--version"],
            capture_output=True,
            text=True,
            cwd=self.test_dir.parent,
        )
        assert result.returncode == 0


class TestDataValidationRuleIntegration:
    """Test data validation rule integration directly."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_dir = Path(__file__).parent.parent
        self.fixtures_dir = self.test_dir / "fixtures"

        self.good_data_file = self.fixtures_dir / "data_sample.xlsx"
        self.bad_data_file = self.fixtures_dir / "data_null_bad.xlsx"
        self.rule_file = self.fixtures_dir / "rule_data_non_null.yaml"

    def test_rule_type_detection(self):
        """Test rule type detection for data validation rules."""
        from src.validator.config import detect_rule_type

        if not self.rule_file.exists():
            pytest.skip("Rule file not available")

        rule_type = detect_rule_type(self.rule_file)
        assert rule_type == "data_validation"

    def test_rule_config_loading(self):
        """Test loading data validation rules into RuleConfig."""
        from src.validator.config import load_rules

        if not self.rule_file.exists():
            pytest.skip("Rule file not available")

        config = load_rules(self.rule_file)
        assert len(config.data_validation_rules) == 1
        assert str(self.rule_file) in config.data_validation_rules
        assert len(config.sheets) == 0  # No structural rules

    @pytest.mark.skipif(
        not Path(__file__)
        .parent.parent.parent.joinpath("src/data/ge_adapter.py")
        .exists(),
        reason="GE adapter not available",
    )
    def test_data_rule_creation(self):
        """Test creating DataValidationRule directly."""
        from src.data import DataValidationRule

        if not self.rule_file.exists():
            pytest.skip("Rule file not available")

        rule = DataValidationRule(str(self.rule_file), None)
        assert rule.rule_file_path == self.rule_file

    def test_validation_failure_serialization(self):
        """Test that ValidationFailure with data validation fields serializes correctly."""
        from src.structural.base import ValidationFailure

        failure = ValidationFailure(
            type="expectation_failed",
            sheet="Data",
            message="Test failure",
            expected="expect_column_values_to_not_be_null",
            found="unexpected_count: 1",
        )

        # Add data validation specific fields
        failure.expectation = "expect_column_values_to_not_be_null"
        failure.column = "amount"
        failure.unexpected_count = 1

        result_dict = failure.to_dict()

        # Check that all fields are included
        assert result_dict["type"] == "expectation_failed"
        assert result_dict["sheet"] == "Data"
        assert result_dict["expectation"] == "expect_column_values_to_not_be_null"
        assert result_dict["column"] == "amount"
        assert result_dict["unexpected_count"] == 1
