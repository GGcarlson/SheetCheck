"""Tests for DataDiffRule."""

from pathlib import Path
from src.data.data_diff_rule import DataDiffRule


def test_data_diff_rule_detects_changes():
    """Test that DataDiffRule detects cell changes between workbooks."""
    rule = DataDiffRule("Sheet1", None)
    
    old_path = Path("tests/fixtures/old_small.xlsx")
    new_path = Path("tests/fixtures/new_small_changed.xlsx")
    
    failures = rule.run_diff(old_path, new_path)
    
    # Should detect 4 changes: 3 cell changes + 1 row added
    assert len(failures) == 4
    
    # Check cell changes
    cell_changes = [f for f in failures if f.type == "cell_changed"]
    assert len(cell_changes) == 3
    
    # Check specific cell changes
    price_change = next(f for f in cell_changes if f.cell == "C3")
    assert price_change.expected == "2"
    assert price_change.found == "2.25"
    assert price_change.sheet == "Sheet1"
    
    quantity_change = next(f for f in cell_changes if f.cell == "D4")
    assert quantity_change.expected == "150"
    assert quantity_change.found == "175"
    
    active_change = next(f for f in cell_changes if f.cell == "E4")
    assert active_change.expected == "False"
    assert active_change.found == "True"
    
    # Check row addition
    row_additions = [f for f in failures if f.type == "row_added"]
    assert len(row_additions) == 1
    assert "ID=5" in row_additions[0].message


def test_data_diff_rule_to_dict():
    """Test that validation failures convert properly to dictionary format."""
    rule = DataDiffRule("Sheet1", None)
    
    old_path = Path("tests/fixtures/old_small.xlsx")
    new_path = Path("tests/fixtures/new_small_changed.xlsx")
    
    failures = rule.run_diff(old_path, new_path)
    
    # Test JSON serialization for cell change
    cell_change = next(f for f in failures if f.type == "cell_changed")
    failure_dict = cell_change.to_dict()
    
    expected_keys = {"type", "sheet", "cell", "message", "fix_hint", "expected", "found"}
    assert expected_keys.issubset(set(failure_dict.keys()))
    
    assert failure_dict["type"] == "cell_changed"
    assert failure_dict["sheet"] == "Sheet1"
    assert "cell" in failure_dict
    assert "expected" in failure_dict
    assert "found" in failure_dict


def test_data_diff_rule_no_differences():
    """Test that DataDiffRule returns no failures when files are identical."""
    rule = DataDiffRule("Sheet1", None)
    
    old_path = Path("tests/fixtures/old_small.xlsx")
    
    # Compare file with itself
    failures = rule.run_diff(old_path, old_path)
    
    # Should find no differences
    assert len(failures) == 0


def test_data_diff_rule_handles_nonexistent_file():
    """Test that DataDiffRule handles missing files gracefully."""
    rule = DataDiffRule("Sheet1", None)
    
    old_path = Path("tests/fixtures/old_small.xlsx")
    missing_path = Path("tests/fixtures/nonexistent.xlsx")
    
    failures = rule.run_diff(old_path, missing_path)
    
    # Should return error failure
    assert len(failures) == 1
    assert failures[0].type == "diff_error"
    assert "xlcompare failed" in failures[0].message