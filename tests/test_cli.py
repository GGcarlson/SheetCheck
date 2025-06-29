import subprocess
import sys
from pathlib import Path


def _run(*args):
    """Run the validator CLI with given arguments."""
    return subprocess.run(
        [sys.executable, "-m", "validator", *args],
        capture_output=True, text=True
    )


def test_help():
    """Test that --help shows usage information."""
    result = _run("--help")
    assert "Usage: validator" in result.stdout
    assert result.returncode == 0


def test_version():
    """Test that --version shows version information."""
    result = _run("--version")
    assert "validator, version" in result.stdout
    assert result.returncode == 0


def test_missing_workbook():
    """Test that missing workbook argument shows error."""
    result = _run()
    assert result.returncode != 0
    assert "Missing argument" in result.stderr or "Usage:" in result.stderr


def test_nonexistent_workbook():
    """Test that nonexistent workbook file shows error."""
    result = _run("nonexistent.xlsx")
    assert result.returncode != 0
    assert "does not exist" in result.stderr.lower() or "no such file" in result.stderr.lower()