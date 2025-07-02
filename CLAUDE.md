# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# SheetCheck - Excel Validation Tool

SheetCheck is a comprehensive Excel/spreadsheet validation tool that provides structural, data, and visual testing capabilities for auditing Excel workbooks. The tool is **production-ready** with extensive functionality implemented and tested.

## Architecture Overview

SheetCheck follows a modular validation architecture with three distinct validation types:

### Validation Pipeline
```
CLI Entry → Rule Engine → [Structural | Data | Visual] → Reporter Factory → [JSON|XML|Markdown]
```

**Core modules:**
- `src/validator/cli.py` - Main CLI entry point with Click framework
- `src/validator/config.py` - YAML rule configuration parsing with auto-detection
- `src/structural/` - Excel structure validation (sheets, formulas, conditional formatting, objects)
- `src/data/` - Data validation via Great Expectations integration + diff comparison
- `src/visual/` - Multi-platform screenshot capture and pixel-diff comparison
- `src/reporter/` - Multi-format report generation with factory pattern

### Rule System Architecture
The rule system uses **automatic type detection** based on YAML content:

**Structural Rules** (`rules/default.yaml`):
```yaml
sheets:
  Summary:
    must_exist: true
    cells:
      B2:
        formula: "=SUM(Data!B2:B10)"
    expect_cf_rules:
      - range: "C2:C50"
        type: "colorScale"
```

**Data Validation Rules**:
```yaml
rule_type: "data_validation"  # Explicit type marker
target:
  sheet: "Data"
expectations:
  - expectation_type: "expect_column_values_to_not_be_null"
    kwargs:
      column: "id"
validation:
  success_threshold: 0.95
```

### Registry Pattern Implementation
- **Structural Rules**: `src/structural/base.py` defines `Rule` abstract base class with registry discovery
- **Reporters**: `src/reporter/factory.py` uses factory pattern for multi-format output
- **Visual Renderers**: Auto-detection between COM (Windows) and HTML+Puppeteer (cross-platform)

## Development Commands

```bash
# Installation and setup
pip install -e .[dev]             # Development installation with all dependencies

# Code quality (run these before commits)
black src/ tests/                 # Format code (88-char line length)
flake8 src/ tests/                # Lint code
mypy src/                         # Type checking (strict mode)

# Testing - comprehensive test suite with 3,815 lines
pytest                            # Run all tests (19 test files)
pytest --cov=src --cov-report=xml # Run with coverage reporting
pytest tests/structural/          # Run structural validation tests
pytest tests/data/                # Run data validation tests  
pytest tests/visual/              # Run visual comparison tests
pytest tests/test_cli.py -v       # Run CLI integration tests

# Single test execution examples
pytest tests/structural/test_formula_rule.py::test_formula_match -v
pytest tests/data/test_ge_adapter.py::test_non_null_validation -v

# CLI usage - production ready
validator --help                           # Show all options
validator --version                        # Show version info
validator workbook.xlsx                    # Basic validation with default rules
validator workbook.xlsx --rules custom.yaml --report json,xml,md
validator old.xlsx new.xlsx --mode diff   # Workbook comparison mode
validator workbook.xlsx --update-baseline # Update visual baselines
```

## Key Implementation Details

### CLI Interface (`src/validator/cli.py`)
- **Dual mode support**: `validate` (single workbook) vs `diff` (comparison)
- **Auto-renderer selection**: `--renderer auto|com|html` with platform detection
- **Flexible reporting**: `--report json,xml,md,markdown` (comma-separated)
- **Baseline management**: `--update-baseline` flag for visual testing

### Configuration System (`src/validator/config.py`)
- **Auto-detection**: Automatically detects structural vs data validation rules
- **Mixed rule support**: Single YAML can contain multiple rule types
- **Error handling**: Comprehensive `RuleConfigError` with actionable messages

### Great Expectations Integration (`src/data/ge_adapter.py`)
- **Full GE compatibility**: Supports complete expectation suite
- **Success thresholds**: Configurable validation pass rates (e.g., 95% of rows)
- **Excel-to-DataFrame**: Automatic conversion with sheet targeting
- **Unified error format**: Converts GE results to `ValidationFailure` objects

### Visual Testing System
- **Multi-platform**: `src/visual/capture.py` with automatic renderer selection
- **Windows COM**: `src/visual/capture_com.py` using xlwings + PIL for native Excel rendering
- **Cross-platform HTML**: `src/visual/capture_mcp.py` with Puppeteer MCP integration
- **Pixel comparison**: `src/visual/pixel_diff.py` with configurable thresholds and diff overlays

### MCP Integration
```bash
# Start Puppeteer MCP server for visual testing
./start-puppeteer-mcp.sh        # Automated startup script
# Server runs at http://localhost:8085
# Tools: mcp__puppeteer__navigate, mcp__puppeteer__screenshot, etc.
```

## Test Architecture and Fixtures

**Test organization** (`tests/`):
- `fixtures/` - Excel test files and YAML rules for all validation types
- `structural/` - Tests for sheet, formula, conditional formatting, object validation
- `data/` - Great Expectations integration and data diff testing
- `visual/` - Screenshot capture and pixel comparison testing
- `reporter/` - Multi-format report generation testing

**Key test fixtures**:
- `tests/fixtures/good_sheet.xlsx` - Valid workbook for positive testing
- `tests/fixtures/formula_mismatch.xlsx` - Broken formulas for negative testing
- `tests/fixtures/rule_*.yaml` - Various rule configurations for testing

## Performance and Scalability

- **Target performance**: ≤15 seconds for 50MB workbooks
- **Memory management**: Proper cleanup of temporary files and resources
- **Dependency handling**: Optional dependencies with graceful fallbacks
- **CI/CD ready**: GitHub Actions workflow with browser installation

## Error Handling Patterns

All validation failures use the unified `ValidationFailure` dataclass:
```python
@dataclass
class ValidationFailure:
    type: str                    # Failure category
    sheet: str = ""             # Target sheet
    cell: str = ""              # Specific cell (if applicable)
    message: str = ""           # Human-readable description
    fix_hint: str = ""          # Actionable repair suggestion
    expected: Union[str, Dict] = ""  # Expected value/state
    found: Optional[Union[str, Dict]] = ""  # Actual value/state
```

## Issue Management Protocol

**CRITICAL**: When completing GitHub issues, ALWAYS add verification comments following this structure:

### Required Issue Comment Structure:
1. **Working Examples** - Show actual CLI commands and outputs
2. **Test Results** - Include pytest output demonstrating functionality
3. **Code Quality** - Confirm black/flake8/mypy pass
4. **Definition of Done** - Check off all issue requirements with ✅
5. **Files Changed** - List all modified/created files

### Example Verification Comment:
```markdown
## ✅ Issue #X Complete - [Feature Name] Implementation

### Working Examples
```bash
# Show actual commands and outputs here
validator workbook.xlsx --rules new-rule.yaml
# [Actual output]
```

### Test Results
```bash
pytest tests/new_feature/ -v
# [Actual pytest output]
```

### Code Quality
- ✅ Black formatting: `black src/ tests/` - no changes needed
- ✅ Flake8 linting: `flake8 src/ tests/` - all checks pass  
- ✅ MyPy typing: `mypy src/` - no type errors

### Definition of Done
- ✅ Feature implemented as specified
- ✅ Tests written and passing
- ✅ Documentation updated
- ✅ Error handling implemented

### Files Changed
- `src/new_module.py` - Core implementation
- `tests/test_new_module.py` - Test coverage
- `README.md` - Usage documentation

Ready for next issues! 🚀
```

This verification pattern ensures complete documentation and prevents regressions.