"""Pixel-level visual comparison utility for PNG images."""

import math
from pathlib import Path
from typing import Optional, Tuple, Union

try:
    from PIL import Image  # type: ignore
except ImportError:
    Image = None  # type: ignore


def diff_png(
    baseline_path: Union[str, Path],
    actual_path: Union[str, Path],
    threshold: float = 0.02,
    diff_output_path: Optional[Union[str, Path]] = None,
) -> float:
    """Compare two PNG images pixel by pixel and return difference ratio.

    Compares two PNG images and calculates the percentage of pixels that differ
    beyond the specified threshold. Optionally generates a diff overlay image
    highlighting the differences.

    Args:
        baseline_path: Path to the baseline/expected PNG image
        actual_path: Path to the actual/captured PNG image
        threshold: Sensitivity threshold (0.0-1.0). Lower values are more sensitive.
                  Default 0.02 means pixels must differ by >2% to count as different.
        diff_output_path: Optional path to save diff overlay image showing differences

    Returns:
        Float ratio (0.0-1.0) representing percentage of differing pixels.
        0.0 = identical images, 1.0 = completely different images

    Raises:
        ImportError: If PIL (Pillow) is not available
        FileNotFoundError: If baseline or actual image files don't exist
        ValueError: If images have different dimensions or invalid threshold
        RuntimeError: If image processing fails

    Example:
        >>> diff_ratio = diff_png("baseline.png", "actual.png", threshold=0.02)
        >>> if diff_ratio > 0.01:  # More than 1% different
        ...     print(f"Images differ by {diff_ratio:.2%}")
        >>>
        >>> # Generate diff overlay
        >>> diff_png("baseline.png", "actual.png", diff_output_path="diff.png")
    """
    # Validate PIL dependency
    if Image is None:
        raise ImportError("PIL (Pillow) is required for image comparison")

    # Validate threshold
    if not 0.0 <= threshold <= 1.0:
        raise ValueError(f"Threshold must be between 0.0 and 1.0, got {threshold}")

    # Convert paths to Path objects
    baseline_path = Path(baseline_path)
    actual_path = Path(actual_path)
    if diff_output_path:
        diff_output_path = Path(diff_output_path)

    # Validate input files exist
    if not baseline_path.exists():
        raise FileNotFoundError(f"Baseline image not found: {baseline_path}")
    if not actual_path.exists():
        raise FileNotFoundError(f"Actual image not found: {actual_path}")

    try:
        # Load images
        baseline_img = Image.open(baseline_path).convert("RGBA")
        actual_img = Image.open(actual_path).convert("RGBA")

        # Validate dimensions match
        if baseline_img.size != actual_img.size:
            raise ValueError(
                f"Image dimensions don't match: "
                f"baseline {baseline_img.size} vs actual {actual_img.size}"
            )

        width, height = baseline_img.size
        total_pixels = width * height

        # If images are identical, return early
        if list(baseline_img.getdata()) == list(actual_img.getdata()):
            if diff_output_path:
                # Ensure output directory exists
                diff_output_path.parent.mkdir(parents=True, exist_ok=True)
                # Create blank diff image for identical images
                diff_img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
                diff_img.save(diff_output_path, "PNG")
            return 0.0

        # Compare pixels and count differences
        baseline_pixels = baseline_img.getdata()
        actual_pixels = actual_img.getdata()

        diff_pixels = []
        different_pixel_count = 0

        for i, (baseline_pixel, actual_pixel) in enumerate(
            zip(baseline_pixels, actual_pixels)
        ):
            # Calculate pixel difference using Euclidean distance in RGBA space
            pixel_diff = _calculate_pixel_difference(baseline_pixel, actual_pixel)

            # Check if difference exceeds threshold
            is_different = pixel_diff > threshold

            if is_different:
                different_pixel_count += 1

            # Prepare diff pixel for overlay image
            if diff_output_path:
                if is_different:
                    # Highlight different pixels in red with intensity based on diff
                    intensity = min(255, int(pixel_diff * 255))
                    diff_pixels.append((intensity, 0, 0, 255))
                else:
                    # Keep original pixel but make it semi-transparent
                    r, g, b, a = (
                        actual_pixel if len(actual_pixel) == 4 else (*actual_pixel, 255)
                    )
                    diff_pixels.append((r, g, b, a // 4))

        # Generate diff overlay image if requested
        if diff_output_path:
            diff_img = Image.new("RGBA", (width, height))
            diff_img.putdata(diff_pixels)

            # Ensure output directory exists
            diff_output_path.parent.mkdir(parents=True, exist_ok=True)
            diff_img.save(diff_output_path, "PNG")

        # Calculate and return difference ratio
        diff_ratio = different_pixel_count / total_pixels
        return float(diff_ratio)

    except Exception as e:
        if isinstance(e, (ImportError, FileNotFoundError, ValueError)):
            raise
        else:
            raise RuntimeError(f"Image comparison failed: {e}") from e


def _calculate_pixel_difference(
    pixel1: Tuple[int, ...], pixel2: Tuple[int, ...]
) -> float:
    """Calculate normalized difference between two RGBA pixels.

    Uses Euclidean distance in RGBA color space, normalized to 0.0-1.0 range.

    Args:
        pixel1: First pixel as (R, G, B, A) tuple
        pixel2: Second pixel as (R, G, B, A) tuple

    Returns:
        Normalized difference value (0.0 = identical, 1.0 = maximally different)
    """
    # Ensure both pixels have RGBA components
    p1 = pixel1 if len(pixel1) == 4 else (*pixel1, 255)
    p2 = pixel2 if len(pixel2) == 4 else (*pixel2, 255)

    # Calculate Euclidean distance in RGBA space
    r_diff = (p1[0] - p2[0]) ** 2
    g_diff = (p1[1] - p2[1]) ** 2
    b_diff = (p1[2] - p2[2]) ** 2
    a_diff = (p1[3] - p2[3]) ** 2

    euclidean_distance = math.sqrt(r_diff + g_diff + b_diff + a_diff)

    # Normalize to 0.0-1.0 range (max possible distance is sqrt(4 * 255^2))
    max_distance = math.sqrt(4 * 255 * 255)
    normalized_diff = euclidean_distance / max_distance

    return normalized_diff


def is_diff_supported() -> bool:
    """Check if pixel difference comparison is supported.

    Returns:
        True if PIL (Pillow) is available, False otherwise
    """
    return Image is not None
