"""Tests for ReporterFactory and create_reporters function."""

import tempfile
from pathlib import Path

import pytest

from src.reporter.factory import ReporterFactory, create_reporters
from src.reporter.json_reporter import JSONReporter
from src.reporter.xml_reporter import XMLReporter
from src.reporter.markdown_reporter import MarkdownReporter


def test_reporter_factory_get_available_formats():
    """Test getting list of available formats."""
    formats = ReporterFactory.get_available_formats()
    
    assert "json" in formats
    assert "xml" in formats
    assert "md" in formats
    assert "markdown" in formats


def test_reporter_factory_create_json_reporter():
    """Test creating JSON reporter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        reporter = ReporterFactory.create_reporter("json", output_dir)
        
        assert isinstance(reporter, JSONReporter)
        assert reporter.output_dir == output_dir


def test_reporter_factory_create_xml_reporter():
    """Test creating XML reporter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        reporter = ReporterFactory.create_reporter("xml", output_dir)
        
        assert isinstance(reporter, XMLReporter)
        assert reporter.output_dir == output_dir


def test_reporter_factory_create_markdown_reporter():
    """Test creating Markdown reporter."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        reporter = ReporterFactory.create_reporter("md", output_dir)
        
        assert isinstance(reporter, MarkdownReporter)
        assert reporter.output_dir == output_dir


def test_reporter_factory_create_markdown_reporter_long_name():
    """Test creating Markdown reporter with 'markdown' name."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        reporter = ReporterFactory.create_reporter("markdown", output_dir)
        
        assert isinstance(reporter, MarkdownReporter)


def test_reporter_factory_case_insensitive():
    """Test that format names are case insensitive."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        
        reporter1 = ReporterFactory.create_reporter("JSON", output_dir)
        reporter2 = ReporterFactory.create_reporter("Xml", output_dir)
        reporter3 = ReporterFactory.create_reporter("MD", output_dir)
        
        assert isinstance(reporter1, JSONReporter)
        assert isinstance(reporter2, XMLReporter)
        assert isinstance(reporter3, MarkdownReporter)


def test_reporter_factory_invalid_format():
    """Test that invalid format raises ValueError."""
    with pytest.raises(ValueError, match="Unsupported format 'invalid'"):
        ReporterFactory.create_reporter("invalid")


def test_reporter_factory_default_output_dir():
    """Test creating reporter with default output directory."""
    reporter = ReporterFactory.create_reporter("json")
    
    assert isinstance(reporter, JSONReporter)
    assert reporter.output_dir == Path("reports")


def test_create_reporters_single_format():
    """Test creating reporters from single format string."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        reporters = create_reporters("json", output_dir)
        
        assert len(reporters) == 1
        assert isinstance(reporters[0], JSONReporter)


def test_create_reporters_multiple_formats():
    """Test creating reporters from multiple format string."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        reporters = create_reporters("json,xml,md", output_dir)
        
        assert len(reporters) == 3
        assert isinstance(reporters[0], JSONReporter)
        assert isinstance(reporters[1], XMLReporter)  
        assert isinstance(reporters[2], MarkdownReporter)


def test_create_reporters_with_spaces():
    """Test creating reporters with spaces in format string."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        reporters = create_reporters("json, xml , md", output_dir)
        
        assert len(reporters) == 3
        assert isinstance(reporters[0], JSONReporter)
        assert isinstance(reporters[1], XMLReporter)
        assert isinstance(reporters[2], MarkdownReporter)


def test_create_reporters_empty_segments():
    """Test creating reporters ignoring empty segments."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir)
        reporters = create_reporters("json,,xml,", output_dir)
        
        assert len(reporters) == 2
        assert isinstance(reporters[0], JSONReporter)
        assert isinstance(reporters[1], XMLReporter)


def test_create_reporters_invalid_format():
    """Test that invalid format in list raises ValueError."""
    with pytest.raises(ValueError, match="Unsupported format 'invalid'"):
        create_reporters("json,invalid,xml")


def test_create_reporters_default_output_dir():
    """Test creating reporters with default output directory."""
    reporters = create_reporters("json")
    
    assert len(reporters) == 1
    assert isinstance(reporters[0], JSONReporter)
    assert reporters[0].output_dir == Path("reports")