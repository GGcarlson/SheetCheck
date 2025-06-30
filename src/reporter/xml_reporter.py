"""XML format reporter."""

import xml.etree.ElementTree as ET
from typing import List, TYPE_CHECKING

from .base import BaseReporter

if TYPE_CHECKING:
    from ..structural.base import ValidationFailure


class XMLReporter(BaseReporter):
    """Reporter that generates XML format output."""
    
    @property
    def file_extension(self) -> str:
        """File extension for XML reports."""
        return "xml"
    
    def generate_report(
        self,
        structural_failures: List["ValidationFailure"],
        data_failures: List["ValidationFailure"],
        visual_failures: List["ValidationFailure"],
    ) -> str:
        """Generate XML report content.
        
        Args:
            structural_failures: List of structural validation failures
            data_failures: List of data validation failures
            visual_failures: List of visual validation failures
            
        Returns:
            XML report content as string
        """
        root = ET.Element("ValidationResults")
        
        # Add structural failures
        structural_elem = ET.SubElement(root, "StructuralFailures")
        for failure in structural_failures:
            self._add_failure_element(structural_elem, failure)
            
        # Add data failures
        data_elem = ET.SubElement(root, "DataFailures")
        for failure in data_failures:
            self._add_failure_element(data_elem, failure)
            
        # Add visual failures
        visual_elem = ET.SubElement(root, "VisualFailures")
        for failure in visual_failures:
            self._add_failure_element(visual_elem, failure)
        
        # Convert to string with proper formatting
        ET.indent(root, space="  ", level=0)
        return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(
            root, encoding="unicode"
        )
    
    def _add_failure_element(self, parent: ET.Element, failure: "ValidationFailure") -> None:
        """Add a failure element to the parent XML element.
        
        Args:
            parent: Parent XML element
            failure: ValidationFailure to add
        """
        failure_elem = ET.SubElement(parent, "Failure")
        failure_dict = failure.to_dict()
        
        for key, value in failure_dict.items():
            if value is not None and value != "":
                elem = ET.SubElement(failure_elem, key)
                if isinstance(value, dict):
                    # Handle nested dictionaries by converting to string
                    elem.text = str(value)
                else:
                    elem.text = str(value)