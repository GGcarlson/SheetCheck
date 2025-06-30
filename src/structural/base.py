"""Base classes for structural validation rules."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union

from openpyxl import Workbook


@dataclass
class ValidationFailure:
    """Represents a validation failure."""

    type: str
    sheet: str = ""
    cell: str = ""
    message: str = ""
    fix_hint: str = ""
    expected: Union[str, Dict[str, Any]] = ""
    found: Optional[Union[str, Dict[str, Any]]] = ""
    range: str = ""
    object: str = ""
    tolerance: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for JSON output."""
        result: Dict[str, Any] = {"type": self.type}
        if self.sheet:
            result["sheet"] = self.sheet
        if self.cell:
            result["cell"] = self.cell
        if self.range:
            result["range"] = self.range
        if self.object:
            result["object"] = self.object
        if self.message:
            result["message"] = self.message
        if self.fix_hint:
            result["fix_hint"] = self.fix_hint

        # Handle expected field (can be string or dict, include if not empty)
        if self.expected:
            result["expected"] = self.expected

        # Handle found field (can be string, dict, or None)
        # Include found field if it's not the default empty string
        if self.found != "":
            result["found"] = self.found

        # Include tolerance if specified
        if self.tolerance is not None:
            result["tolerance"] = self.tolerance

        # Include any additional custom attributes for data validation
        for attr_name in [
            "expectation",
            "column",
            "unexpected_count",
            "observed_value",
        ]:
            if hasattr(self, attr_name):
                attr_value = getattr(self, attr_name)
                if attr_value is not None:
                    result[attr_name] = attr_value

        return result


class Rule(ABC):
    """Abstract base class for all validation rules."""

    def __init__(self, sheet_name: str, sheet_config: Any) -> None:
        """Initialize rule with sheet name and configuration.

        Args:
            sheet_name: Name of the sheet this rule applies to
            sheet_config: Configuration object for this sheet
        """
        self.sheet_name = sheet_name
        self.sheet_config = sheet_config

    @abstractmethod
    def run(self, workbook: Workbook) -> List[ValidationFailure]:
        """Execute the validation rule against a workbook.

        Args:
            workbook: The Excel workbook to validate

        Returns:
            List of validation failures, empty if validation passes
        """
        pass
