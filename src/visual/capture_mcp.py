"""MCP screenshot capture utility for cross-platform Excel automation."""

import platform
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, Union

# MCP server interaction capabilities
try:
    import mcp__puppeteer__navigate  # type: ignore
    import mcp__puppeteer__screenshot  # type: ignore

    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False


def capture_sheet_png(
    wb_path: Union[str, Path], sheet_name: str, png_path: Union[str, Path]
) -> None:
    """Capture a screenshot of an Excel sheet and save as PNG using MCP.

    Uses HTML rendering via SheetJS + Puppeteer MCP screenshot capture for
    cross-platform Excel visual validation.

    Args:
        wb_path: Path to the Excel workbook file
        sheet_name: Name of the sheet to capture
        png_path: Output path for the PNG screenshot

    Raises:
        ImportError: If MCP Puppeteer tools are not available
        FileNotFoundError: If the workbook file doesn't exist or Node.js not found
        ValueError: If the sheet name doesn't exist in the workbook
        RuntimeError: If HTML generation or screenshot capture fails

    Example:
        >>> capture_sheet_png("workbook.xlsx", "Dashboard", "screenshot.png")
    """
    # Check MCP availability
    if not MCP_AVAILABLE:
        raise ImportError(
            "MCP Puppeteer tools are not available. "
            "Ensure MCP server is running and permissions are set."
        )

    # Convert paths to Path objects for consistent handling
    wb_path = Path(wb_path)
    png_path = Path(png_path)

    # Validate workbook file exists
    if not wb_path.exists():
        raise FileNotFoundError(f"Workbook file not found: {wb_path}")

    # Ensure output directory exists
    png_path.parent.mkdir(parents=True, exist_ok=True)

    # Create temporary HTML file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".html", delete=False, encoding="utf-8"
    ) as temp_html:
        temp_html_path = Path(temp_html.name)

    try:
        # Generate HTML from Excel using Node.js helper
        html_content = _generate_html_from_excel(wb_path, sheet_name)

        # Write HTML to temporary file
        temp_html_path.write_text(html_content, encoding="utf-8")

        # Capture screenshot using MCP
        _capture_html_screenshot(temp_html_path, png_path)

        # Verify the PNG file was created and has reasonable size
        if not png_path.exists():
            raise RuntimeError(f"Failed to create PNG file: {png_path}")

        file_size = png_path.stat().st_size
        if file_size < 10000:  # Less than 10KB suggests an error
            raise RuntimeError(
                f"PNG file appears corrupted or too small (size: {file_size} bytes). "
                f"Expected size >10KB for Excel screenshots."
            )

    except Exception as e:
        # Clean up any partially created files on error
        if png_path.exists():
            try:
                png_path.unlink()
            except OSError:
                pass

        # Re-raise with context
        if isinstance(e, (ImportError, FileNotFoundError, ValueError)):
            raise
        else:
            raise RuntimeError(f"MCP screenshot capture failed: {e}") from e

    finally:
        # Clean up temporary HTML file
        if temp_html_path.exists():
            try:
                temp_html_path.unlink()
            except OSError:
                pass


def _generate_html_from_excel(wb_path: Path, sheet_name: str) -> str:
    """Generate HTML content from Excel sheet using Node.js SheetJS helper.

    Args:
        wb_path: Path to Excel workbook
        sheet_name: Name of sheet to convert

    Returns:
        HTML content as string

    Raises:
        FileNotFoundError: If Node.js or render_html.js not found
        ValueError: If sheet name doesn't exist
        RuntimeError: If HTML generation fails
    """
    # Find the Node.js helper script
    project_root = Path(__file__).parent.parent.parent
    render_script = project_root / "tools" / "render_html.js"

    if not render_script.exists():
        raise FileNotFoundError(
            f"Node.js helper script not found: {render_script}. "
            f"Ensure tools/render_html.js exists."
        )

    try:
        # Run Node.js script to convert Excel to HTML
        cmd = ["node", str(render_script), str(wb_path), sheet_name]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,  # 30-second timeout
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip()
            if "Sheet" in error_msg and "not found" in error_msg:
                raise ValueError(f"Sheet '{sheet_name}' not found in workbook")
            elif "File not found" in error_msg:
                raise FileNotFoundError(f"Workbook file not found: {wb_path}")
            else:
                raise RuntimeError(f"HTML generation failed: {error_msg}")

        html_content = result.stdout
        if not html_content.strip():
            raise RuntimeError("HTML generation produced empty output")

        return html_content

    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"HTML generation timed out after 30 seconds for sheet '{sheet_name}'"
        )
    except FileNotFoundError as e:
        if "node" in str(e).lower():
            raise FileNotFoundError(
                "Node.js not found. Please install Node.js to use MCP capture. "
                "Visit: https://nodejs.org/"
            ) from e
        raise


def _capture_html_screenshot(html_path: Path, png_path: Path) -> None:
    """Capture screenshot of HTML file using Puppeteer MCP.

    Args:
        html_path: Path to HTML file to screenshot
        png_path: Output path for PNG screenshot

    Raises:
        RuntimeError: If MCP navigation or screenshot fails
    """
    try:
        # Convert to file:// URL for Puppeteer
        file_url = html_path.as_uri()

        # Navigate to HTML file using MCP
        navigate_result = mcp__puppeteer__navigate(file_url)

        # Check if navigation was successful
        if not _is_mcp_success(navigate_result):
            raise RuntimeError(f"Failed to navigate to HTML file: {navigate_result}")

        # Capture full-page screenshot using MCP
        screenshot_options = {"path": str(png_path), "fullPage": True, "type": "png"}

        screenshot_result = mcp__puppeteer__screenshot(screenshot_options)

        # Check if screenshot was successful
        if not _is_mcp_success(screenshot_result):
            raise RuntimeError(f"Failed to capture screenshot: {screenshot_result}")

    except Exception as e:
        if "mcp__puppeteer__" in str(e):
            raise RuntimeError(
                f"MCP Puppeteer tool error: {e}. "
                f"Ensure MCP server is running at http://localhost:8085"
            ) from e
        raise


def _is_mcp_success(result: Any) -> bool:
    """Check if MCP tool result indicates success.

    Args:
        result: Result from MCP tool call

    Returns:
        True if success, False otherwise
    """
    # Handle different possible result formats
    if isinstance(result, dict):
        # Look for common success indicators
        if result.get("success") is True:
            return True
        if result.get("error"):
            return False
        # If no explicit success/error, assume success if no error field
        return "error" not in result

    # For string results, check for common error patterns
    if isinstance(result, str):
        error_patterns = ["error", "failed", "timeout", "refused"]
        result_lower = result.lower()
        return not any(pattern in result_lower for pattern in error_patterns)

    # For other types, assume success if result exists
    return result is not None


def is_capture_supported() -> bool:
    """Check if MCP screenshot capture is supported.

    Returns:
        True if MCP Puppeteer tools are available, False otherwise
    """
    return MCP_AVAILABLE


def get_renderer_info() -> Dict[str, Any]:
    """Get information about available screenshot renderers.

    Returns:
        Dictionary with renderer availability and platform info
    """
    info = {
        "platform": platform.system(),
        "mcp_available": MCP_AVAILABLE,
        "preferred_renderer": "mcp" if MCP_AVAILABLE else "none",
    }

    # Check for COM availability on Windows  
    if platform.system() == "Windows":
        try:
            from . import capture_com

            info["com_available"] = capture_com.is_capture_supported()
            # MCP module prefers MCP even when COM is available
        except ImportError:
            info["com_available"] = False
    else:
        info["com_available"] = False

    return info
