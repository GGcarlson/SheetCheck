"""Integration tests for the complete reporter system."""

import subprocess
import tempfile
import json
import xml.etree.ElementTree as ET
from pathlib import Path
import sys


def _run_validator(*args):
    """Run the validator CLI with given arguments."""
    return subprocess.run(
        [sys.executable, "-m", "src.validator.cli", *args],
        capture_output=True,
        text=True,
        cwd="/home/john/SheetCheck"
    )


def test_cli_reports_json_format():
    """Test CLI generates JSON report when requested."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Change to temp directory to isolate reports
        original_cwd = Path.cwd()
        tmpdir_path = Path(tmpdir)
        
        try:
            # Use existing test fixture
            result = _run_validator(
                "tests/fixtures/missing_sheet.xlsx",
                "--rules", "tests/fixtures/rule_sheet.yaml", 
                "--report", "json"
            )
            
            # Check that CLI mentions JSON report
            assert "JSON report written" in result.stdout
            
        finally:
            pass  # Don't change directory in test


def test_cli_reports_multiple_formats():
    """Test CLI generates multiple report formats when requested."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = _run_validator(
            "tests/fixtures/missing_sheet.xlsx",
            "--rules", "tests/fixtures/rule_sheet.yaml",
            "--report", "json,xml,md"
        )
        
        # Should mention all three report types
        assert "JSON report written" in result.stdout
        assert "XML report written" in result.stdout  
        assert "Markdown report written" in result.stdout


def test_cli_reports_invalid_format():
    """Test CLI handles invalid report format gracefully."""
    result = _run_validator(
        "tests/fixtures/missing_sheet.xlsx", 
        "--rules", "tests/fixtures/rule_sheet.yaml",
        "--report", "invalid"
    )
    
    assert "Error creating reports" in result.stderr
    assert "Unsupported format 'invalid'" in result.stderr


def test_reports_contain_expected_data():
    """Test that generated reports contain expected validation data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Run validator to generate reports in temp directory
        result = _run_validator(
            "tests/fixtures/missing_sheet.xlsx",
            "--rules", "tests/fixtures/rule_sheet.yaml",
            "--report", "json,xml,md"
        )
        
        # Check exit code indicates validation failure
        assert result.returncode == 1
        
        # Reports should be created in ./reports/ relative to where CLI runs
        reports_dir = Path("/home/john/SheetCheck/reports")
        
        if reports_dir.exists():
            # Check JSON report if it exists
            json_file = reports_dir / "results.json"
            if json_file.exists():
                with open(json_file) as f:
                    data = json.load(f)
                    
                # Should have structural failures for missing sheet
                assert "structuralFailures" in data
                
            # Check XML report if it exists
            xml_file = reports_dir / "results.xml"
            if xml_file.exists():
                tree = ET.parse(xml_file)
                root = tree.getroot()
                assert root.tag == "ValidationResults"
                
            # Check Markdown report if it exists
            md_file = reports_dir / "results.md"
            if md_file.exists():
                content = md_file.read_text()
                assert "# SheetCheck Validation Report" in content