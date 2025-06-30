"""Markdown format reporter."""

from typing import List, TYPE_CHECKING

from .base import BaseReporter

if TYPE_CHECKING:
    from ..structural.base import ValidationFailure


class MarkdownReporter(BaseReporter):
    """Reporter that generates human-readable Markdown format output."""
    
    @property
    def file_extension(self) -> str:
        """File extension for Markdown reports."""
        return "md"
    
    def generate_report(
        self,
        structural_failures: List["ValidationFailure"],
        data_failures: List["ValidationFailure"],
        visual_failures: List["ValidationFailure"],
    ) -> str:
        """Generate Markdown report content.
        
        Args:
            structural_failures: List of structural validation failures
            data_failures: List of data validation failures
            visual_failures: List of visual validation failures
            
        Returns:
            Markdown report content as string
        """
        report_lines = []
        
        # Title and summary
        total_failures = len(structural_failures) + len(data_failures) + len(visual_failures)
        report_lines.append("# SheetCheck Validation Report")
        report_lines.append("")
        
        if total_failures == 0:
            report_lines.append("✅ **All validations passed!**")
            report_lines.append("")
        else:
            report_lines.append(f"❌ **{total_failures} validation failure(s) found**")
            report_lines.append("")
            
            # Summary table
            report_lines.append("## Summary")
            report_lines.append("")
            report_lines.append("| Category | Failures |")
            report_lines.append("|----------|----------|")
            report_lines.append(f"| Structural | {len(structural_failures)} |")
            report_lines.append(f"| Data | {len(data_failures)} |")
            report_lines.append(f"| Visual | {len(visual_failures)} |")
            report_lines.append(f"| **Total** | **{total_failures}** |")
            report_lines.append("")
        
        # Structural failures section
        if structural_failures:
            report_lines.append("## Structural Failures")
            report_lines.append("")
            for i, failure in enumerate(structural_failures, 1):
                report_lines.extend(self._format_failure(i, failure))
                report_lines.append("")
        
        # Data failures section
        if data_failures:
            report_lines.append("## Data Validation Failures")
            report_lines.append("")
            for i, failure in enumerate(data_failures, 1):
                report_lines.extend(self._format_failure(i, failure))
                report_lines.append("")
        
        # Visual failures section
        if visual_failures:
            report_lines.append("## Visual Validation Failures")
            report_lines.append("")
            for i, failure in enumerate(visual_failures, 1):
                report_lines.extend(self._format_failure(i, failure))
                report_lines.append("")
        
        return "\n".join(report_lines)
    
    def _format_failure(self, index: int, failure: "ValidationFailure") -> List[str]:
        """Format a single failure for Markdown output.
        
        Args:
            index: Failure index number
            failure: ValidationFailure to format
            
        Returns:
            List of formatted lines for this failure
        """
        lines = []
        lines.append(f"### {index}. {failure.type}")
        lines.append("")
        
        # Add failure details
        if hasattr(failure, 'message') and failure.message:
            lines.append(f"**Message:** {failure.message}")
            lines.append("")
            
        if hasattr(failure, 'sheet') and failure.sheet:
            lines.append(f"**Sheet:** {failure.sheet}")
            
        if hasattr(failure, 'cell') and failure.cell:
            lines.append(f"**Cell:** {failure.cell}")
            
        if hasattr(failure, 'range') and failure.range:
            lines.append(f"**Range:** {failure.range}")
            
        if hasattr(failure, 'object') and failure.object:
            lines.append(f"**Object:** {failure.object}")
            
        if hasattr(failure, 'expected') and failure.expected:
            lines.append(f"**Expected:** `{failure.expected}`")
            
        if hasattr(failure, 'found') and failure.found is not None:
            lines.append(f"**Found:** `{failure.found}`")
            
        if hasattr(failure, 'fix_hint') and failure.fix_hint:
            lines.append("")
            lines.append(f"💡 **Fix hint:** {failure.fix_hint}")
        
        return lines