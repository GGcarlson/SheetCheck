"""Tests for JSONReporter class."""

import json
import tempfile
from pathlib import Path

from src.reporter.json_reporter import JSONReporter
from src.structural.base import ValidationFailure


def test_json_reporter_file_extension():
    """Test that JSONReporter returns correct file extension."""
    reporter = JSONReporter()
    assert reporter.file_extension == "json"


def test_json_reporter_default_filename():
    """Test that JSONReporter returns correct default filename."""
    reporter = JSONReporter()
    assert reporter.default_filename == "results.json"


def test_json_reporter_generate_empty_report():
    """Test JSON report generation with no failures."""
    reporter = JSONReporter()
    
    result = reporter.generate_report([], [], [])
    data = json.loads(result)
    
    assert data == {
        "structuralFailures": [],
        "dataFailures": [],
        "visualFailures": []
    }


def test_json_reporter_generate_report_with_failures():
    """Test JSON report generation with various failures."""
    reporter = JSONReporter()
    
    structural_failures = [
        ValidationFailure(
            type="sheet_missing",
            sheet="TestSheet",
            message="Sheet does not exist"
        )
    ]
    
    data_failures = [
        ValidationFailure(
            type="data_validation",
            sheet="DataSheet",
            cell="A1",
            message="Value is null"
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
    data = json.loads(result)
    
    assert len(data["structuralFailures"]) == 1
    assert len(data["dataFailures"]) == 1
    assert len(data["visualFailures"]) == 1
    
    assert data["structuralFailures"][0]["type"] == "sheet_missing"
    assert data["structuralFailures"][0]["sheet"] == "TestSheet"
    assert data["dataFailures"][0]["cell"] == "A1"


def test_json_reporter_write_to_file():
    """Test writing JSON report to file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        reporter = JSONReporter(output_dir)
        
        failures = [
            ValidationFailure(
                type="test_failure",
                message="Test message"
            )
        ]
        
        output_path = reporter.write_to_file(failures, [], [])
        
        assert output_path.exists()
        assert output_path.name == "results.json"
        
        with open(output_path) as f:
            data = json.load(f)
            
        assert len(data["structuralFailures"]) == 1
        assert data["structuralFailures"][0]["type"] == "test_failure"


def test_json_reporter_custom_filename():
    """Test writing JSON report with custom filename."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        reporter = JSONReporter(output_dir)
        
        output_path = reporter.write_to_file([], [], [], "custom.json")
        
        assert output_path.exists()
        assert output_path.name == "custom.json"