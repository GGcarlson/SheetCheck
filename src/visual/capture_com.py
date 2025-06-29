"""COM screenshot capture utility for Windows Excel automation."""

import platform
from pathlib import Path
from typing import Union

try:
    import xlwings as xw
except ImportError:
    xw = None

try:
    from PIL import ImageGrab  # type: ignore
except ImportError:
    ImageGrab = None  # type: ignore


def capture_sheet_png(
    wb_path: Union[str, Path], sheet_name: str, png_path: Union[str, Path]
) -> None:
    """Capture a screenshot of an Excel sheet and save as PNG.

    Uses Windows COM automation via xlwings to open Excel, activate the specified
    sheet, capture a screenshot to clipboard, and save as PNG using PIL.

    Args:
        wb_path: Path to the Excel workbook file
        sheet_name: Name of the sheet to capture
        png_path: Output path for the PNG screenshot

    Raises:
        NotImplementedError: If not running on Windows platform
        ImportError: If required dependencies (xlwings, PIL) are not available
        FileNotFoundError: If the workbook file doesn't exist
        ValueError: If the sheet name doesn't exist in the workbook
        RuntimeError: If screenshot capture fails

    Example:
        >>> capture_sheet_png("workbook.xlsx", "Dashboard", "screenshot.png")
    """
    # Check platform compatibility
    if platform.system() != "Windows":
        raise NotImplementedError(
            "COM screenshot capture is only supported on Windows platforms"
        )

    # Check dependencies
    if xw is None:
        raise ImportError("xlwings is required for COM screenshot capture")

    if ImageGrab is None:
        raise ImportError("PIL (Pillow) is required for clipboard image processing")

    # Convert paths to Path objects for consistent handling
    wb_path = Path(wb_path)
    png_path = Path(png_path)

    # Validate workbook file exists
    if not wb_path.exists():
        raise FileNotFoundError(f"Workbook file not found: {wb_path}")

    # Ensure output directory exists
    png_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Open Excel application with xlwings
        with xw.App(visible=True) as app:
            # Open the workbook
            wb = app.books.open(str(wb_path.absolute()))

            try:
                # Activate the specified sheet
                try:
                    sheet = wb.sheets[sheet_name]
                    sheet.activate()
                except KeyError:
                    available_sheets = [s.name for s in wb.sheets]
                    raise ValueError(
                        f"Sheet '{sheet_name}' not found. "
                        f"Available sheets: {available_sheets}"
                    )

                # Ensure the sheet window is active and properly sized
                # Select a range to ensure the sheet is fully loaded
                sheet.range("A1").select()

                # Capture the entire sheet as picture to clipboard
                # Uses Excel's COM API to copy the active sheet as a picture
                sheet.api.UsedRange.CopyPicture(
                    Appearance=1, Format=2  # xlScreen  # xlPicture
                )

                # Get image from clipboard using PIL
                image = ImageGrab.grabclipboard()  # type: ignore

                if image is None:
                    raise RuntimeError(
                        "Failed to capture image from clipboard. "
                        "Ensure Excel is properly displaying the sheet."
                    )

                # Save the image as PNG
                image.save(str(png_path), "PNG")  # type: ignore

                # Verify the PNG file was created and has reasonable size
                if not png_path.exists():
                    raise RuntimeError(f"Failed to create PNG file: {png_path}")

                file_size = png_path.stat().st_size
                if file_size < 1000:  # Less than 1KB suggests an error
                    raise RuntimeError(
                        f"PNG file appears corrupted or empty (size: {file_size} bytes)"
                    )

            finally:
                # Always close the workbook
                wb.close()

    except Exception as e:
        # Clean up any partially created files on error
        if png_path.exists():
            try:
                png_path.unlink()
            except OSError:
                pass

        # Re-raise the original exception with additional context
        if isinstance(
            e, (NotImplementedError, ImportError, FileNotFoundError, ValueError)
        ):
            raise
        else:
            raise RuntimeError(f"Screenshot capture failed: {e}") from e


def is_capture_supported() -> bool:
    """Check if COM screenshot capture is supported on this platform.

    Returns:
        True if Windows platform with required dependencies, False otherwise
    """
    return platform.system() == "Windows" and xw is not None and ImageGrab is not None
