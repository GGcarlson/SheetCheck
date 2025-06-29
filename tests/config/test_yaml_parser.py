"""Tests for YAML rule parser."""

import pytest

from src.validator.config import (
    load_rules,
    RuleConfigError,
    RuleConfig,
    SheetCfg,
)


def test_good_yaml(tmp_path):
    """Test successful parsing of valid YAML."""
    yml = tmp_path / "good.yaml"
    yml.write_text("sheets:\n  Sheet1:\n    must_exist: true\n")
    cfg = load_rules(yml)
    assert cfg.sheets["Sheet1"].must_exist is True


def test_bad_yaml(tmp_path):
    """Test error handling for malformed YAML."""
    yml = tmp_path / "bad.yaml"
    yml.write_text("not: valid: yaml: [unclosed")
    with pytest.raises(RuleConfigError):
        load_rules(yml)


def test_missing_file():
    """Test error handling for missing file."""
    with pytest.raises(RuleConfigError, match="Rules file not found"):
        load_rules("nonexistent.yaml")


def test_empty_file(tmp_path):
    """Test handling of empty YAML file."""
    yml = tmp_path / "empty.yaml"
    yml.write_text("")
    cfg = load_rules(yml)
    assert cfg.sheets == {}


def test_no_sheets_section(tmp_path):
    """Test YAML without sheets section."""
    yml = tmp_path / "no_sheets.yaml"
    yml.write_text("other_config: value\n")
    cfg = load_rules(yml)
    assert cfg.sheets == {}


def test_complex_sheet_config(tmp_path):
    """Test complex sheet configuration with all fields."""
    yml = tmp_path / "complex.yaml"
    yml.write_text(
        """
sheets:
  Summary:
    must_exist: true
    cells:
      A1: "Title"
      B2: 42
    expect_cf_rules:
      - type: "highlight"
        range: "A1:B10"
  Data:
    must_exist: false
    cells: {}
    expect_cf_rules: []
"""
    )
    cfg = load_rules(yml)

    # Check Summary sheet
    summary = cfg.sheets["Summary"]
    assert summary.must_exist is True
    assert summary.cells["A1"] == "Title"
    assert summary.cells["B2"] == 42
    assert len(summary.expect_cf_rules) == 1
    assert summary.expect_cf_rules[0]["type"] == "highlight"

    # Check Data sheet
    data = cfg.sheets["Data"]
    assert data.must_exist is False
    assert data.cells == {}
    assert data.expect_cf_rules == []


def test_invalid_sheet_config(tmp_path):
    """Test error handling for invalid sheet configuration."""
    yml = tmp_path / "invalid.yaml"
    yml.write_text("sheets:\n  Sheet1: not_a_dict\n")
    with pytest.raises(RuleConfigError, match="must be a dictionary"):
        load_rules(yml)


def test_default_values(tmp_path):
    """Test that default values are applied correctly."""
    yml = tmp_path / "minimal.yaml"
    yml.write_text("sheets:\n  Sheet1: {}\n")
    cfg = load_rules(yml)

    sheet = cfg.sheets["Sheet1"]
    assert sheet.must_exist is False
    assert sheet.cells == {}
    assert sheet.expect_cf_rules == []


def test_load_actual_default_rules():
    """Test loading the actual default.yaml file."""
    cfg = load_rules("rules/default.yaml")
    assert "Summary" in cfg.sheets
    assert cfg.sheets["Summary"].must_exist is True


def test_dataclass_types():
    """Test that the correct dataclass types are returned."""
    cfg = RuleConfig()
    assert isinstance(cfg, RuleConfig)

    sheet_cfg = SheetCfg(must_exist=True)
    assert isinstance(sheet_cfg, SheetCfg)
    assert sheet_cfg.must_exist is True
    assert sheet_cfg.cells == {}
    assert sheet_cfg.expect_cf_rules == []
