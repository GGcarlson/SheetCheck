"""Configuration management for SheetCheck validator."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Union

import yaml


class RuleConfigError(Exception):
    """Exception raised when rule configuration is invalid."""

    pass


@dataclass
class SheetCfg:
    """Configuration for a single sheet validation."""

    must_exist: bool = False
    cells: Dict[str, Any] = field(default_factory=dict)
    expect_cf_rules: List[Dict] = field(default_factory=list)


@dataclass
class RuleConfig:
    """Complete rule configuration for workbook validation."""

    sheets: Dict[str, SheetCfg] = field(default_factory=dict)
    # Data validation rules (Great Expectations)
    data_validation_rules: List[str] = field(default_factory=list)


def detect_rule_type(path: Union[str, Path]) -> str:
    """Detect the type of rule from a YAML file.

    Args:
        path: Path to YAML rule file

    Returns:
        Rule type: "data_validation" or "structural"

    Raises:
        RuleConfigError: If file cannot be read or parsed
    """
    path = Path(path)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        raise RuleConfigError(f"Rules file not found: {path}")
    except yaml.YAMLError as e:
        raise RuleConfigError(f"Invalid YAML in {path}: {e}")
    except Exception as e:
        raise RuleConfigError(f"Error reading {path}: {e}")

    if data is None:
        return "structural"  # Default to structural for empty files

    # Check for explicit rule_type
    rule_type = data.get("rule_type")
    if rule_type == "data_validation":
        return "data_validation"
    elif rule_type == "structural":
        return "structural"

    # Auto-detect based on content
    if "expectations" in data:
        return "data_validation"
    elif "sheets" in data:
        return "structural"

    # Default to structural for unknown format
    return "structural"


def load_rules(path: Union[str, Path]) -> RuleConfig:
    """Load and parse rule configuration from YAML file.

    Handles both structural validation rules and data validation rules.
    Data validation rules are identified by rule_type: "data_validation"
    or presence of "expectations" field.

    Args:
        path: Path to YAML rule file

    Returns:
        RuleConfig object with parsed configuration

    Raises:
        RuleConfigError: If YAML is invalid or configuration is malformed
    """
    path = Path(path)

    # Detect rule type
    rule_type = detect_rule_type(path)

    if rule_type == "data_validation":
        # For data validation rules, just store the file path
        return RuleConfig(sheets={}, data_validation_rules=[str(path)])

    # Handle structural rules (original logic)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except FileNotFoundError:
        raise RuleConfigError(f"Rules file not found: {path}")
    except yaml.YAMLError as e:
        raise RuleConfigError(f"Invalid YAML in {path}: {e}")
    except Exception as e:
        raise RuleConfigError(f"Error reading {path}: {e}")

    if data is None:
        data = {}

    try:
        # Parse sheets configuration
        sheets = {}
        if "sheets" in data:
            for sheet_name, sheet_config in data["sheets"].items():
                if not isinstance(sheet_config, dict):
                    raise RuleConfigError(
                        f"Sheet configuration for '{sheet_name}' must be a "
                        "dictionary"
                    )

                sheets[sheet_name] = SheetCfg(
                    must_exist=sheet_config.get("must_exist", False),
                    cells=sheet_config.get("cells", {}),
                    expect_cf_rules=sheet_config.get("expect_cf_rules", []),
                )

        return RuleConfig(sheets=sheets, data_validation_rules=[])

    except Exception as e:
        raise RuleConfigError(f"Error parsing configuration from {path}: {e}")
