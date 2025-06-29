# SheetCheck - Excel Validation Tool

## Project Overview
SheetCheck is a comprehensive Excel/spreadsheet validation tool that provides structural, data, and visual testing capabilities.

## Architecture
- `src/structural/` - Validates spreadsheet structure (headers, column types, required fields)
- `src/data/` - Validates data content (ranges, formats, business rules)  
- `src/visual/` - Visual regression testing via screenshot comparison
- `src/cli.py` - Command-line interface entry point

## Testing
- `tests/fixtures/` - Small XLSX files and PNG baselines for testing
- `tests/structural/` - Unit tests for structural validation
- `baselines/` - Golden screenshots and JSON object dumps for comparison

## Configuration
- `rules/default.yaml` - Default validation rule bundles
- `.claude/settings.json` - Tool allow-list for Claude Code integration

## Development Commands
```bash
# Install dependencies
pip install -e .[dev]

# Run tests
pytest

# Run linting
black src/ tests/
flake8 src/ tests/

# Type checking
mypy src/
```

## Notes
This is the initial empty skeleton (Ticket #0) to provide Claude with a stable anchor for development.