import json
import sys
from pathlib import Path
from typing import List

import click
from openpyxl import load_workbook
from openpyxl.workbook import Workbook

from . import __version__
from .config import load_rules, RuleConfigError, RuleConfig
from ..structural import get_structural_rules
from ..structural.base import ValidationFailure
from ..data import DataValidationRule


@click.command()
@click.argument("workbook", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--rules",
    type=click.Path(exists=True, path_type=Path),
    default="rules/default.yaml",
    help="Rules YAML file (default: rules/default.yaml)",
)
@click.option(
    "--renderer",
    type=click.Choice(["auto", "com", "html"]),
    default="auto",
    help="Screenshot renderer (default: auto)",
)
@click.option(
    "--report",
    default="json,md",
    help="Comma-separated reports: json,md,xml (default: json,md)",
)
@click.version_option(version=__version__, prog_name="validator")
def main(workbook: Path, rules: Path, renderer: str, report: str) -> None:
    """Validate an Excel workbook."""
    click.echo(f"Validating workbook: {workbook}")
    click.echo(f"Using rules: {rules}")
    click.echo(f"Renderer: {renderer}")
    click.echo(f"Reports: {report}")

    # Load and validate rule configuration
    try:
        config = load_rules(rules)
        total_rules = len(config.sheets) + len(config.data_validation_rules)
        click.echo(f"Loaded {total_rules} rule(s)")

        if config.sheets:
            click.echo(f"  - {len(config.sheets)} structural rule(s)")
            for sheet_name, sheet_cfg in config.sheets.items():
                if sheet_cfg.must_exist:
                    click.echo(f"    - {sheet_name}: must exist")

        if config.data_validation_rules:
            click.echo(
                f"  - {len(config.data_validation_rules)} data validation rule(s)"
            )
            for rule_path in config.data_validation_rules:
                click.echo(f"    - {Path(rule_path).name}")

    except RuleConfigError as e:
        click.echo(f"Error loading rules: {e}", err=True)
        raise click.Abort()

    # Load the workbook
    try:
        wb = load_workbook(workbook, data_only=False)
        sheet_list = ", ".join(wb.sheetnames)
        click.echo(f"Loaded workbook with {len(wb.sheetnames)} sheet(s): {sheet_list}")
    except Exception as e:
        click.echo(f"Error loading workbook: {e}", err=True)
        raise click.Abort()

    # Run validation
    structural_failures = run_structural_validation(wb, config)
    data_failures = run_data_validation(wb, config)

    all_failures = structural_failures + data_failures

    # Generate reports
    reports = report.split(",")
    if "json" in reports:
        output_json_report(structural_failures, data_failures)

    # Set exit code based on validation results
    if all_failures:
        error_count = len(all_failures)
        click.echo(f"Validation failed with {error_count} error(s)")
        if structural_failures:
            click.echo(f"  - {len(structural_failures)} structural failure(s)")
        if data_failures:
            click.echo(f"  - {len(data_failures)} data validation failure(s)")
        sys.exit(1)
    else:
        click.echo("Validation passed")
        sys.exit(0)


def run_structural_validation(
    workbook: Workbook, config: RuleConfig
) -> List[ValidationFailure]:
    """Run all structural validation rules.

    Args:
        workbook: The loaded Excel workbook
        config: The rule configuration

    Returns:
        List of validation failures
    """
    failures = []
    rule_registry = get_structural_rules()

    for sheet_name, sheet_config in config.sheets.items():
        # Check if sheet existence rule should be applied
        if hasattr(sheet_config, "must_exist") and sheet_config.must_exist:
            rule_class = rule_registry.get("sheet_exists")
            if rule_class:
                rule = rule_class(sheet_name, sheet_config)
                sheet_failures = rule.run(workbook)
                failures.extend(sheet_failures)

        # Check if cell formula validation should be applied
        if hasattr(sheet_config, "cells") and sheet_config.cells:
            rule_class = rule_registry.get("cell_formula")
            if rule_class:
                rule = rule_class(sheet_name, sheet_config)
                sheet_failures = rule.run(workbook)
                failures.extend(sheet_failures)

        # Check if conditional formatting validation should be applied
        if hasattr(sheet_config, "expect_cf_rules") and sheet_config.expect_cf_rules:
            rule_class = rule_registry.get("conditional_formatting")
            if rule_class:
                rule = rule_class(sheet_name, sheet_config)
                sheet_failures = rule.run(workbook)
                failures.extend(sheet_failures)

        # Check if object position validation should be applied
        if hasattr(sheet_config, "objects") and sheet_config.objects:
            rule_class = rule_registry.get("object_position")
            if rule_class:
                rule = rule_class(sheet_name, sheet_config)
                sheet_failures = rule.run(workbook)
                failures.extend(sheet_failures)

    return failures


def run_data_validation(
    workbook: Workbook, config: RuleConfig
) -> List[ValidationFailure]:
    """Run all data validation rules using Great Expectations.

    Args:
        workbook: The loaded Excel workbook
        config: The rule configuration

    Returns:
        List of validation failures from data validation
    """
    failures = []

    for rule_path in config.data_validation_rules:
        try:
            # Create data validation rule and run it
            data_rule = DataValidationRule(rule_path, None)
            rule_failures = data_rule.run(workbook)
            failures.extend(rule_failures)

            click.echo(f"Data validation completed for {Path(rule_path).name}")
            if rule_failures:
                click.echo(f"  - Found {len(rule_failures)} failure(s)")
            else:
                click.echo("  - Passed")

        except Exception as e:
            click.echo(f"Error running data validation for {rule_path}: {e}", err=True)
            failures.append(
                ValidationFailure(
                    type="data_validation_error",
                    message=f"Failed to run data validation: {e}",
                    fix_hint=f"Check rule file: {rule_path}",
                )
            )

    return failures


def output_json_report(
    structural_failures: List[ValidationFailure], data_failures: List[ValidationFailure]
) -> None:
    """Output validation results in JSON format.

    Args:
        structural_failures: List of structural validation failures
        data_failures: List of data validation failures
    """
    result = {
        "structuralFailures": [failure.to_dict() for failure in structural_failures],
        "dataFailures": [failure.to_dict() for failure in data_failures],
    }

    json_output = json.dumps(result, indent=2)

    # Write to results.json file
    with open("results.json", "w") as f:
        f.write(json_output)

    click.echo("JSON report written to results.json")


if __name__ == "__main__":
    main()
