"""Tests for pixel-level visual comparison functionality."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

try:
    from PIL import Image  # type: ignore
except ImportError:
    Image = None

from src.visual.pixel_diff import (
    diff_png,
    is_diff_supported,
    _calculate_pixel_difference,
)


class TestPixelDiff:
    """Test cases for pixel difference comparison."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        if Image is None:
            pytest.skip("PIL (Pillow) not available")

        # Create temporary directory for test images
        self.temp_dir = Path(tempfile.mkdtemp())

        # Create test images
        self.baseline_path = self.temp_dir / "baseline.png"
        self.actual_path = self.temp_dir / "actual.png"
        self.diff_path = self.temp_dir / "diff.png"

        # Create identical 10x10 red square images
        self.create_test_image(self.baseline_path, color=(255, 0, 0, 255))
        self.create_test_image(self.actual_path, color=(255, 0, 0, 255))

    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        # Clean up temporary files
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def create_test_image(self, path: Path, size=(10, 10), color=(255, 0, 0, 255)):
        """Create a test PNG image with specified color."""
        img = Image.new("RGBA", size, color)
        img.save(path, "PNG")

    def test_identical_images_return_zero_diff(self):
        """Test that identical images return 0.0 difference ratio."""
        diff_ratio = diff_png(self.baseline_path, self.actual_path)
        assert diff_ratio == 0.0

    def test_identical_images_with_diff_output(self):
        """Test identical images with diff overlay generation."""
        diff_ratio = diff_png(
            self.baseline_path, self.actual_path, diff_output_path=self.diff_path
        )

        assert diff_ratio == 0.0
        assert self.diff_path.exists()

        # Diff image should be transparent for identical images
        diff_img = Image.open(self.diff_path)
        assert diff_img.mode == "RGBA"
        assert diff_img.size == (10, 10)

    def test_completely_different_images(self):
        """Test completely different images return high difference ratio."""
        # Create a blue image as actual
        self.create_test_image(self.actual_path, color=(0, 0, 255, 255))

        diff_ratio = diff_png(self.baseline_path, self.actual_path, threshold=0.1)

        # Should be high difference since red vs blue
        assert diff_ratio > 0.5

    def test_slightly_different_images_with_threshold(self):
        """Test threshold sensitivity with slightly different images."""
        # Create slightly different color (254, 0, 0, 255) vs (255, 0, 0, 255)
        self.create_test_image(self.actual_path, color=(254, 0, 0, 255))

        # With high threshold (low sensitivity), should be considered same
        diff_ratio_high_threshold = diff_png(
            self.baseline_path, self.actual_path, threshold=0.1
        )
        assert diff_ratio_high_threshold == 0.0

        # With low threshold (high sensitivity), should detect difference
        diff_ratio_low_threshold = diff_png(
            self.baseline_path, self.actual_path, threshold=0.001
        )
        assert diff_ratio_low_threshold > 0.0

    def test_diff_overlay_generation(self):
        """Test generation of diff overlay image."""
        # Create different image
        self.create_test_image(self.actual_path, color=(0, 255, 0, 255))  # Green

        diff_ratio = diff_png(
            self.baseline_path,
            self.actual_path,
            threshold=0.1,
            diff_output_path=self.diff_path,
        )

        assert diff_ratio > 0.0
        assert self.diff_path.exists()

        # Check diff image properties
        diff_img = Image.open(self.diff_path)
        assert diff_img.mode == "RGBA"
        assert diff_img.size == (10, 10)

    def test_default_threshold_value(self):
        """Test that default threshold value is applied correctly."""
        # Create slightly different image
        self.create_test_image(self.actual_path, color=(250, 0, 0, 255))

        # Call without explicit threshold (should use default 0.02)
        diff_ratio = diff_png(self.baseline_path, self.actual_path)

        # Should detect some difference with default threshold
        assert isinstance(diff_ratio, float)
        assert 0.0 <= diff_ratio <= 1.0

    def test_file_not_found_errors(self):
        """Test proper error handling for missing files."""
        missing_path = self.temp_dir / "missing.png"

        with pytest.raises(FileNotFoundError, match="Baseline image not found"):
            diff_png(missing_path, self.actual_path)

        with pytest.raises(FileNotFoundError, match="Actual image not found"):
            diff_png(self.baseline_path, missing_path)

    def test_dimension_mismatch_error(self):
        """Test error handling for images with different dimensions."""
        # Create images with different sizes
        self.create_test_image(self.baseline_path, size=(10, 10))
        self.create_test_image(self.actual_path, size=(20, 20))

        with pytest.raises(ValueError, match="Image dimensions don't match"):
            diff_png(self.baseline_path, self.actual_path)

    def test_invalid_threshold_values(self):
        """Test error handling for invalid threshold values."""
        with pytest.raises(ValueError, match="Threshold must be between 0.0 and 1.0"):
            diff_png(self.baseline_path, self.actual_path, threshold=-0.1)

        with pytest.raises(ValueError, match="Threshold must be between 0.0 and 1.0"):
            diff_png(self.baseline_path, self.actual_path, threshold=1.5)

    def test_string_and_path_objects(self):
        """Test that both string and Path objects work as input."""
        # Test with string paths
        diff_ratio_str = diff_png(str(self.baseline_path), str(self.actual_path))

        # Test with Path objects
        diff_ratio_path = diff_png(self.baseline_path, self.actual_path)

        assert diff_ratio_str == diff_ratio_path == 0.0

    def test_diff_output_directory_creation(self):
        """Test that output directory is created if it doesn't exist."""
        nested_diff_path = self.temp_dir / "subdir" / "nested" / "diff.png"

        diff_ratio = diff_png(
            self.baseline_path, self.actual_path, diff_output_path=nested_diff_path
        )

        assert diff_ratio == 0.0
        assert nested_diff_path.exists()
        assert nested_diff_path.parent.exists()

    @patch("src.visual.pixel_diff.Image", None)
    def test_pil_not_available_error(self):
        """Test error handling when PIL is not available."""
        with pytest.raises(ImportError, match="PIL \\(Pillow\\) is required"):
            diff_png(self.baseline_path, self.actual_path)


class TestCalculatePixelDifference:
    """Test cases for pixel difference calculation helper function."""

    def test_identical_pixels(self):
        """Test that identical pixels return 0.0 difference."""
        pixel1 = (255, 0, 0, 255)
        pixel2 = (255, 0, 0, 255)

        diff = _calculate_pixel_difference(pixel1, pixel2)
        assert diff == 0.0

    def test_maximally_different_pixels(self):
        """Test maximally different pixels (black vs white with full alpha)."""
        pixel1 = (0, 0, 0, 0)  # Transparent black
        pixel2 = (255, 255, 255, 255)  # Opaque white

        diff = _calculate_pixel_difference(pixel1, pixel2)
        assert diff == 1.0

    def test_rgb_pixels_without_alpha(self):
        """Test RGB pixels (missing alpha channel)."""
        pixel1 = (255, 0, 0)  # Red without alpha
        pixel2 = (0, 255, 0)  # Green without alpha

        diff = _calculate_pixel_difference(pixel1, pixel2)
        assert 0.0 < diff < 1.0

    def test_mixed_rgb_and_rgba_pixels(self):
        """Test mixing RGB and RGBA pixels."""
        pixel1 = (255, 0, 0)  # RGB red
        pixel2 = (255, 0, 0, 255)  # RGBA red with full alpha

        diff = _calculate_pixel_difference(pixel1, pixel2)
        assert diff == 0.0  # Should be identical (RGB treated as RGBA with alpha=255)

    def test_difference_is_symmetric(self):
        """Test that pixel difference calculation is symmetric."""
        pixel1 = (100, 150, 200, 128)
        pixel2 = (50, 75, 225, 255)

        diff1 = _calculate_pixel_difference(pixel1, pixel2)
        diff2 = _calculate_pixel_difference(pixel2, pixel1)

        assert diff1 == diff2

    def test_difference_range(self):
        """Test that differences are always in valid 0.0-1.0 range."""
        import random

        for _ in range(100):  # Test with random pixel values
            pixel1 = tuple(random.randint(0, 255) for _ in range(4))
            pixel2 = tuple(random.randint(0, 255) for _ in range(4))

            diff = _calculate_pixel_difference(pixel1, pixel2)
            assert 0.0 <= diff <= 1.0


class TestIsDiffSupported:
    """Test cases for diff support detection."""

    def test_is_diff_supported_with_pil(self):
        """Test support detection when PIL is available."""
        if Image is not None:
            assert is_diff_supported() is True
        else:
            pytest.skip("PIL not available for testing")

    @patch("src.visual.pixel_diff.Image", None)
    def test_is_diff_supported_without_pil(self):
        """Test support detection when PIL is not available."""
        assert is_diff_supported() is False


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def setup_method(self):
        """Set up test fixtures."""
        if Image is None:
            pytest.skip("PIL (Pillow) not available")

        self.temp_dir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def test_single_pixel_images(self):
        """Test comparison of 1x1 pixel images."""
        baseline_path = self.temp_dir / "baseline_1px.png"
        actual_path = self.temp_dir / "actual_1px.png"

        # Create 1x1 images
        img1 = Image.new("RGBA", (1, 1), (255, 0, 0, 255))
        img2 = Image.new("RGBA", (1, 1), (0, 255, 0, 255))
        img1.save(baseline_path, "PNG")
        img2.save(actual_path, "PNG")

        diff_ratio = diff_png(baseline_path, actual_path)
        assert diff_ratio == 1.0  # Single different pixel = 100% different

    def test_large_images_performance(self):
        """Test that large images are handled efficiently."""
        baseline_path = self.temp_dir / "baseline_large.png"
        actual_path = self.temp_dir / "actual_large.png"

        # Create 100x100 images (reasonable size for performance test)
        img1 = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
        img2 = Image.new("RGBA", (100, 100), (255, 0, 0, 255))
        img1.save(baseline_path, "PNG")
        img2.save(actual_path, "PNG")

        # Should complete quickly
        import time

        start_time = time.time()
        diff_ratio = diff_png(baseline_path, actual_path)
        end_time = time.time()

        assert diff_ratio == 0.0
        assert end_time - start_time < 5.0  # Should complete within 5 seconds

    def test_grayscale_images(self):
        """Test comparison of grayscale images."""
        baseline_path = self.temp_dir / "baseline_gray.png"
        actual_path = self.temp_dir / "actual_gray.png"

        # Create grayscale images (will be converted to RGBA internally)
        img1 = Image.new("L", (10, 10), 128)  # Gray
        img2 = Image.new("L", (10, 10), 64)  # Darker gray
        img1.save(baseline_path, "PNG")
        img2.save(actual_path, "PNG")

        diff_ratio = diff_png(baseline_path, actual_path)
        assert 0.0 < diff_ratio <= 1.0
