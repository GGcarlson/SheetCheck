"""Unified screenshot capture interface with automatic renderer selection."""

import platform
from pathlib import Path
from typing import Dict, Any, Union


def capture_sheet_png(
    wb_path: Union[str, Path],
    sheet_name: str,
    png_path: Union[str, Path],
    renderer: str = "auto",
) -> None:
    """Capture a screenshot of an Excel sheet with automatic renderer selection.

    Automatically selects the best available renderer:
    - Windows: COM (xlwings + PIL) for native Excel rendering
    - Other platforms: MCP (HTML + Puppeteer) for cross-platform support

    Args:
        wb_path: Path to the Excel workbook file
        sheet_name: Name of the sheet to capture
        png_path: Output path for the PNG screenshot
        renderer: Renderer to use ("auto", "com", "mcp")

    Raises:
        ImportError: If no suitable renderer is available
        FileNotFoundError: If the workbook file doesn't exist
        ValueError: If the sheet name doesn't exist in the workbook
        RuntimeError: If screenshot capture fails

    Example:
        >>> capture_sheet_png("workbook.xlsx", "Dashboard", "screenshot.png")
    """
    # Get renderer info to determine best option
    info = get_renderer_info()

    # Select renderer based on preference and availability
    if renderer == "auto":
        selected_renderer = info["preferred_renderer"]
    else:
        selected_renderer = renderer

    # Validate renderer availability
    if selected_renderer == "com":
        if not info.get("com_available", False):
            raise ImportError(
                "COM renderer not available. "
                "Requires Windows platform with xlwings and PIL."
            )
        from . import capture_com

        capture_com.capture_sheet_png(wb_path, sheet_name, png_path)

    elif selected_renderer == "mcp":
        if not info.get("mcp_available", False):
            raise ImportError(
                "MCP renderer not available. "
                "Requires MCP Puppeteer server and tools."
            )
        from . import capture_mcp

        capture_mcp.capture_sheet_png(wb_path, sheet_name, png_path)

    else:
        available_renderers = [
            name for name in ["com", "mcp"] if info.get(f"{name}_available", False)
        ]

        if not available_renderers:
            raise ImportError(
                "No screenshot renderers available. "
                "Install xlwings+PIL (Windows) or setup MCP Puppeteer server."
            )

        raise ValueError(
            f"Invalid renderer '{selected_renderer}'. "
            f"Available: {available_renderers}"
        )


def get_renderer_info() -> Dict[str, Any]:
    """Get information about available screenshot renderers.

    Returns:
        Dictionary with renderer availability and platform info
    """
    info = {
        "platform": platform.system(),
        "com_available": False,
        "mcp_available": False,
        "preferred_renderer": "none",
    }

    # Check COM availability (Windows only)
    if platform.system() == "Windows":
        try:
            from . import capture_com

            info["com_available"] = capture_com.is_capture_supported()
        except ImportError:
            pass

    # Check MCP availability (all platforms)
    try:
        from . import capture_mcp

        info["mcp_available"] = capture_mcp.is_capture_supported()
    except ImportError:
        pass

    # Determine preferred renderer
    if info["com_available"]:
        info["preferred_renderer"] = "com"  # Prefer COM on Windows
    elif info["mcp_available"]:
        info["preferred_renderer"] = "mcp"  # Fallback to MCP

    return info


def is_capture_supported() -> bool:
    """Check if any screenshot capture method is supported.

    Returns:
        True if at least one renderer is available, False otherwise
    """
    info = get_renderer_info()
    return bool(info["com_available"] or info["mcp_available"])
