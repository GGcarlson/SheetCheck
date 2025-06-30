"""Reporter factory for creating appropriate reporter instances."""

from pathlib import Path
from typing import Dict, List, Type

from .base import BaseReporter
from .json_reporter import JSONReporter
from .xml_reporter import XMLReporter
from .markdown_reporter import MarkdownReporter


class ReporterFactory:
    """Factory class for creating reporter instances."""
    
    _REPORTERS: Dict[str, Type[BaseReporter]] = {
        "json": JSONReporter,
        "xml": XMLReporter,
        "md": MarkdownReporter,
        "markdown": MarkdownReporter,
    }
    
    @classmethod
    def get_available_formats(cls) -> List[str]:
        """Get list of available report formats.
        
        Returns:
            List of supported format names
        """
        return list(cls._REPORTERS.keys())
    
    @classmethod
    def create_reporter(cls, format_name: str, output_dir: Path = Path("reports")) -> BaseReporter:
        """Create a reporter instance for the specified format.
        
        Args:
            format_name: Name of the report format (json, xml, md, markdown)
            output_dir: Directory to write reports to
            
        Returns:
            Reporter instance for the specified format
            
        Raises:
            ValueError: If format_name is not supported
        """
        format_name = format_name.lower().strip()
        
        if format_name not in cls._REPORTERS:
            available = ", ".join(cls.get_available_formats())
            raise ValueError(f"Unsupported format '{format_name}'. Available formats: {available}")
        
        reporter_class = cls._REPORTERS[format_name]
        return reporter_class(output_dir)


def create_reporters(format_list: str, output_dir: Path = Path("reports")) -> List[BaseReporter]:
    """Create multiple reporter instances from a comma-separated format list.
    
    Args:
        format_list: Comma-separated list of format names (e.g., "json,md,xml")
        output_dir: Directory to write reports to
        
    Returns:
        List of reporter instances
        
    Raises:
        ValueError: If any format name is not supported
    """
    reporters = []
    formats = [fmt.strip() for fmt in format_list.split(",") if fmt.strip()]
    
    for format_name in formats:
        reporter = ReporterFactory.create_reporter(format_name, output_dir)
        reporters.append(reporter)
    
    return reporters