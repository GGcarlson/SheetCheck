"""JSON format reporter."""

import json
from typing import List, TYPE_CHECKING

from .base import BaseReporter

if TYPE_CHECKING:
    from ..structural.base import ValidationFailure


class JSONReporter(BaseReporter):
    """Reporter that generates JSON format output."""
    
    @property
    def file_extension(self) -> str:
        """File extension for JSON reports."""
        return "json"
    
    def generate_report(
        self,
        structural_failures: List["ValidationFailure"],
        data_failures: List["ValidationFailure"],
        visual_failures: List["ValidationFailure"],
    ) -> str:
        """Generate JSON report content.
        
        Args:
            structural_failures: List of structural validation failures
            data_failures: List of data validation failures
            visual_failures: List of visual validation failures
            
        Returns:
            JSON report content as string
        """
        result = {
            "structuralFailures": [failure.to_dict() for failure in structural_failures],
            "dataFailures": [failure.to_dict() for failure in data_failures],
            "visualFailures": [failure.to_dict() for failure in visual_failures],
        }
        
        return json.dumps(result, indent=2)