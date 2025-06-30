"""Tests for XMLReporter class."""

import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

from src.reporter.xml_reporter import XMLReporter
from src.structural.base import ValidationFailure


def test_xml_reporter_file_extension():
    """Test that XMLReporter returns correct file extension."""
    reporter = XMLReporter()
    assert reporter.file_extension == "xml"


def test_xml_reporter_default_filename():
    """Test that XMLReporter returns correct default filename."""
    reporter = XMLReporter()
    assert reporter.default_filename == "results.xml"


def test_xml_reporter_generate_empty_report():
    """Test XML report generation with no failures."""
    reporter = XMLReporter()
    
    result = reporter.generate_report([], [], [])
    
    # Parse the XML
    root = ET.fromstring(result)
    assert root.tag == "ValidationResults"
    
    # Check that all failure sections exist but are empty
    structural = root.find("StructuralFailures")
    data = root.find("DataFailures") 
    visual = root.find("VisualFailures")
    
    assert structural is not None
    assert data is not None
    assert visual is not None
    
    assert len(structural) == 0
    assert len(data) == 0
    assert len(visual) == 0


def test_xml_reporter_generate_report_with_failures():
    """Test XML report generation with various failures."""
    reporter = XMLReporter()
    
    structural_failures = [
        ValidationFailure(
            type="sheet_missing",
            sheet="TestSheet",
            message="Sheet does not exist",
            fix_hint="Create the sheet"
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
    
    result = reporter.generate_report(structural_failures, data_failures, [])
    
    # Parse the XML
    root = ET.fromstring(result)
    
    # Check structural failures
    structural = root.find("StructuralFailures")
    assert len(structural) == 1
    
    failure = structural.find("Failure")
    assert failure.find("type").text == "sheet_missing"
    assert failure.find("sheet").text == "TestSheet"
    assert failure.find("message").text == "Sheet does not exist"
    assert failure.find("fix_hint").text == "Create the sheet"
    
    # Check data failures
    data = root.find("DataFailures")
    assert len(data) == 1
    
    failure = data.find("Failure")
    assert failure.find("type").text == "data_validation"
    assert failure.find("cell").text == "A1"


def test_xml_reporter_write_to_file():
    """Test writing XML report to file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        reporter = XMLReporter(output_dir)
        
        failures = [
            ValidationFailure(
                type="test_failure",
                message="Test message"
            )
        ]
        
        output_path = reporter.write_to_file(failures, [], [])
        
        assert output_path.exists()
        assert output_path.name == "results.xml"
        
        # Parse and verify the written file
        root = ET.parse(output_path).getroot()
        structural = root.find("StructuralFailures")
        assert len(structural) == 1
        
        failure = structural.find("Failure")
        assert failure.find("type").text == "test_failure"


def test_xml_reporter_handles_complex_data():
    """Test that XML reporter handles complex ValidationFailure data."""
    reporter = XMLReporter()
    
    failure = ValidationFailure(
        type="complex_failure",
        expected={"key": "value"},
        found=None,
        tolerance=5
    )
    
    result = reporter.generate_report([failure], [], [])
    
    root = ET.fromstring(result)
    structural = root.find("StructuralFailures")
    failure_elem = structural.find("Failure")
    
    assert failure_elem.find("type").text == "complex_failure"
    assert failure_elem.find("expected").text == "{'key': 'value'}"
    assert failure_elem.find("found").text == "None"