"""Tests for MarkdownReporter class."""

import tempfile
from pathlib import Path

from src.reporter.markdown_reporter import MarkdownReporter
from src.structural.base import ValidationFailure


def test_markdown_reporter_file_extension():
    """Test that MarkdownReporter returns correct file extension."""
    reporter = MarkdownReporter()
    assert reporter.file_extension == "md"


def test_markdown_reporter_default_filename():
    """Test that MarkdownReporter returns correct default filename."""
    reporter = MarkdownReporter()
    assert reporter.default_filename == "results.md"


def test_markdown_reporter_generate_empty_report():
    """Test Markdown report generation with no failures."""
    reporter = MarkdownReporter()
    
    result = reporter.generate_report([], [], [])
    
    assert "# SheetCheck Validation Report" in result
    assert "✅ **All validations passed!**" in result
    assert "## Summary" not in result  # No summary table for passing cases


def test_markdown_reporter_generate_report_with_failures():
    """Test Markdown report generation with various failures."""
    reporter = MarkdownReporter()
    
    structural_failures = [
        ValidationFailure(
            type="sheet_missing",
            sheet="TestSheet",
            message="Sheet does not exist",
            fix_hint="Create the missing sheet"
        )
    ]
    
    data_failures = [
        ValidationFailure(
            type="data_validation",
            sheet="DataSheet",
            cell="A1",
            message="Value is null",
            expected="non-null value",
            found="null"
        )
    ]
    
    visual_failures = [
        ValidationFailure(
            type="visual_diff",
            sheet="VisualSheet",
            message="Visual difference detected"
        )
    ]
    
    result = reporter.generate_report(structural_failures, data_failures, visual_failures)
    
    # Check main structure
    assert "# SheetCheck Validation Report" in result
    assert "❌ **3 validation failure(s) found**" in result
    
    # Check summary table
    assert "## Summary" in result
    assert "| Structural | 1 |" in result
    assert "| Data | 1 |" in result
    assert "| Visual | 1 |" in result
    assert "| **Total** | **3** |" in result
    
    # Check sections
    assert "## Structural Failures" in result
    assert "## Data Validation Failures" in result
    assert "## Visual Validation Failures" in result
    
    # Check specific failure details
    assert "### 1. sheet_missing" in result
    assert "**Sheet:** TestSheet" in result
    assert "💡 **Fix hint:** Create the missing sheet" in result
    
    assert "**Expected:** `non-null value`" in result
    assert "**Found:** `null`" in result


def test_markdown_reporter_format_failure():
    """Test formatting of individual failures."""
    reporter = MarkdownReporter()
    
    failure = ValidationFailure(
        type="test_failure",
        sheet="Sheet1",
        cell="B2",
        range="A1:C3",
        object="TestObject",
        message="Test failure message",
        expected="expected_value",
        found="found_value",
        fix_hint="How to fix this"
    )
    
    lines = reporter._format_failure(1, failure)
    formatted = "\n".join(lines)
    
    assert "### 1. test_failure" in formatted
    assert "**Message:** Test failure message" in formatted
    assert "**Sheet:** Sheet1" in formatted
    assert "**Cell:** B2" in formatted
    assert "**Range:** A1:C3" in formatted
    assert "**Object:** TestObject" in formatted
    assert "**Expected:** `expected_value`" in formatted
    assert "**Found:** `found_value`" in formatted
    assert "💡 **Fix hint:** How to fix this" in formatted


def test_markdown_reporter_write_to_file():
    """Test writing Markdown report to file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        reporter = MarkdownReporter(output_dir)
        
        failures = [
            ValidationFailure(
                type="test_failure",
                message="Test message"
            )
        ]
        
        output_path = reporter.write_to_file(failures, [], [])
        
        assert output_path.exists()
        assert output_path.name == "results.md"
        
        content = output_path.read_text()
        assert "# SheetCheck Validation Report" in content
        assert "### 1. test_failure" in content


def test_markdown_reporter_handles_none_values():
    """Test that Markdown reporter handles None and empty values gracefully."""
    reporter = MarkdownReporter()
    
    failure = ValidationFailure(
        type="minimal_failure",
        found=None  # Explicitly None
    )
    
    result = reporter.generate_report([failure], [], [])
    
    assert "### 1. minimal_failure" in result
    assert "**Found:** `None`" in result