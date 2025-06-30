# SheetCheck - Excel Validation Tool

![CI](https://github.com/GGcarlson/SheetCheck/workflows/CI/badge.svg)

SheetCheck is a comprehensive Excel/spreadsheet validation tool that provides structural, data, and visual testing capabilities for auditing Excel workbooks.

## Quick Start

### Installation

```bash
# Install in development mode
pip install -e .

# Install with development dependencies
pip install -e .[dev]
```

### Basic Usage

```bash
# Show help
validator --help

# Show version
validator --version

# Validate a workbook with default rules
validator workbook.xlsx

# Use custom rules file
validator workbook.xlsx --rules custom-rules.yaml

# Specify renderer and output formats
validator workbook.xlsx --renderer com --report json,md,xml
```

### Command Options

- `--rules PATH`: Rules YAML file (default: rules/default.yaml)
- `--renderer [auto|com|html]`: Screenshot renderer (default: auto)
- `--report LIST`: Comma-separated reports: json,md,xml (default: json,md)
- `--version`: Show version and exit
- `--help`: Show help message and exit

## Development

See [CLAUDE.md](CLAUDE.md) for development guidance and [PRD.md](PRD.md) for product requirements.

### Running Tests

```bash
# Run all tests
pytest

# Run CLI tests specifically
pytest tests/test_cli.py

# Run with coverage
pytest --cov=src --cov-report=xml
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
flake8 src/ tests/

# Type checking
mypy src/
```

## License

MIT License - see LICENSE file for details.