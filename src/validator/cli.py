import click
from pathlib import Path

from . import __version__
from .config import load_rules, RuleConfigError


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
        click.echo(f"Loaded {len(config.sheets)} sheet rule(s)")
        for sheet_name, sheet_cfg in config.sheets.items():
            if sheet_cfg.must_exist:
                click.echo(f"  - {sheet_name}: must exist")
    except RuleConfigError as e:
        click.echo(f"Error loading rules: {e}", err=True)
        raise click.Abort()

    # TODO: Implement actual validation logic
    click.echo("Validation complete (placeholder implementation)")


if __name__ == "__main__":
    main()
