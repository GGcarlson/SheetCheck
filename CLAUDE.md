# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# SheetCheck - Excel Validation Tool

SheetCheck is a comprehensive Excel/spreadsheet validation tool that provides structural, data, and visual testing capabilities. See `PRD.md` for complete product requirements and success metrics.

## Core Architecture

The project follows a modular validation architecture with three main validation types:

- **Structural validation** (`src/structural/`) - Validates spreadsheet structure like headers, column types, and required fields
- **Data validation** (`src/data/`) - Validates data content including ranges, formats, and business rules  
- **Visual validation** (`src/visual/`) - Performs visual regression testing via screenshot comparison

The CLI entry point (`src/cli.py`) orchestrates these validation modules using Click framework.

## Key Components

- **Rule System**: YAML-based validation rules stored in `rules/` directory, with `default.yaml` as the base ruleset
- **Baseline Management**: `baselines/` contains golden screenshots and JSON object dumps for comparison testing
- **Test Infrastructure**: `tests/fixtures/` holds small XLSX files and PNG baselines for testing validation logic

## Development Commands

```bash
# Setup development environment
pip install -e .[dev]

# Code quality checks (run before commits)
black src/ tests/          # Format code
flake8 src/ tests/          # Lint code  
mypy src/                   # Type checking

# Testing
pytest                      # Run all tests
pytest --cov=src --cov-report=xml  # Run tests with coverage
pytest tests/structural/    # Run specific test module

# CLI usage (once implemented)
sheetcheck validate file.xlsx --rules rules/default.yaml
```

## Performance Requirements

- Target validation runtime: ≤15s for 50MB workbooks
- Support XLSX/XLSM files (openpyxl + xlwings for COM access)
- Pixel-diff visual validation with configurable thresholds
- Multiple output formats: JSON, JUnit XML, Markdown reports

## Development Notes

- Python 3.8+ required, supports through 3.11
- Uses openpyxl for Excel file processing, PyYAML for rule configuration
- Code style: Black formatting with 88-character line length
- Type hints required (mypy strict mode enabled)
- CLI built with Click framework, entry point defined in pyproject.toml
- Future integration: pandas + Great Expectations for data validation
- Screenshot providers: COM (Windows) with HTML+Puppeteer fallback