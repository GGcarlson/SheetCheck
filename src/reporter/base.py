"""Base reporter class and common utilities."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..structural.base import ValidationFailure


class BaseReporter(ABC):
    """Abstract base class for all report generators."""
    
    def __init__(self, output_dir: Path = Path("reports")):
        """Initialize reporter with output directory.
        
        Args:
            output_dir: Directory to write reports to
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    @property
    @abstractmethod
    def file_extension(self) -> str:
        """File extension for this report format."""
        pass
    
    @property
    def default_filename(self) -> str:
        """Default filename for this report format."""
        return f"results.{self.file_extension}"
    
    @abstractmethod
    def generate_report(
        self,
        structural_failures: List["ValidationFailure"],
        data_failures: List["ValidationFailure"], 
        visual_failures: List["ValidationFailure"],
    ) -> str:
        """Generate report content.
        
        Args:
            structural_failures: List of structural validation failures
            data_failures: List of data validation failures
            visual_failures: List of visual validation failures
            
        Returns:
            Generated report content as string
        """
        pass
    
    def write_to_file(
        self,
        structural_failures: List["ValidationFailure"],
        data_failures: List["ValidationFailure"],
        visual_failures: List["ValidationFailure"],
        filename: str = None,
    ) -> Path:
        """Generate and write report to file.
        
        Args:
            structural_failures: List of structural validation failures
            data_failures: List of data validation failures
            visual_failures: List of visual validation failures
            filename: Optional custom filename
            
        Returns:
            Path to the generated report file
        """
        report_content = self.generate_report(
            structural_failures, data_failures, visual_failures
        )
        
        if filename is None:
            filename = self.default_filename
            
        output_path = self.output_dir / filename
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)
            
        return output_path