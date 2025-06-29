"""Structural validation rules and registry."""

from typing import Dict, Type

from .base import Rule
from .conditional import ConditionalFormattingRule
from .formula import CellFormulaRule
from .object_pos import ObjectPositionRule
from .sheet_exists import SheetExistsRule


# Registry of available structural rules
RULE_REGISTRY: Dict[str, Type[Rule]] = {
    "sheet_exists": SheetExistsRule,
    "cell_formula": CellFormulaRule,
    "conditional_formatting": ConditionalFormattingRule,
    "object_position": ObjectPositionRule,
}


def get_structural_rules() -> Dict[str, Type[Rule]]:
    """Get the registry of all available structural validation rules.

    Returns:
        Dictionary mapping rule names to rule classes
    """
    return RULE_REGISTRY.copy()
