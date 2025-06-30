"""Tests for baseline update functionality."""

from pathlib import Path
from unittest.mock import Mock, patch

from src.validator.cli import (
    run_visual_validation,
    get_baseline_path,
    update_baseline_file,
)


class TestRunVisualValidation:
    """Tests for visual validation with baseline management."""

    def test_update_baseline_mode(self, tmp_path):
        """Test updating baselines instead of comparing."""
        # Setup mock workbook and config
        mock_workbook = Mock()
        mock_workbook.sheetnames = ["Sheet1", "Dashboard"]
        mock_config = Mock()

        workbook_path = tmp_path / "test.xlsx"
        workbook_path.write_bytes(b"fake xlsx content")

        # Mock successful capture
        with patch(
            "src.validator.cli.capture.is_capture_supported"
        ) as mock_supported, patch(
            "src.validator.cli.capture.capture_sheet_png"
        ) as mock_capture, patch(
            "src.validator.cli.update_baseline_file"
        ) as mock_update:

            mock_supported.return_value = True

            failures = run_visual_validation(
                mock_workbook, mock_config, workbook_path, "auto", update_baseline=True
            )

            # Should have no failures in update mode
            assert failures == []

            # Should capture screenshots for each sheet
            assert mock_capture.call_count == 2

            # Should update baselines for each sheet
            assert mock_update.call_count == 2

    def test_validation_mode_missing_baseline(self, tmp_path):
        """Test validation mode when baseline is missing."""
        # Setup mock workbook and config
        mock_workbook = Mock()
        mock_workbook.sheetnames = ["Sheet1"]
        mock_config = Mock()

        workbook_path = tmp_path / "test.xlsx"
        workbook_path.write_bytes(b"fake xlsx content")

        with patch(
            "src.validator.cli.capture.is_capture_supported"
        ) as mock_supported, patch(
            "src.validator.cli.capture.capture_sheet_png"
        ), patch(
            "src.validator.cli.get_baseline_path"
        ) as mock_baseline_path:

            mock_supported.return_value = True

            # Mock missing baseline
            mock_baseline = Mock()
            mock_baseline.exists.return_value = False
            mock_baseline_path.return_value = mock_baseline

            failures = run_visual_validation(
                mock_workbook, mock_config, workbook_path, "auto", update_baseline=False
            )

            # Should have one failure for missing baseline
            assert len(failures) == 1
            assert failures[0].type == "visual_baseline_missing"
            assert "missing" in failures[0].message.lower()

    def test_validation_mode_visual_diff(self, tmp_path):
        """Test validation mode when visual difference is detected."""
        # Setup mock workbook and config
        mock_workbook = Mock()
        mock_workbook.sheetnames = ["Sheet1"]
        mock_config = Mock()

        workbook_path = tmp_path / "test.xlsx"
        workbook_path.write_bytes(b"fake xlsx content")

        with patch(
            "src.validator.cli.capture.is_capture_supported"
        ) as mock_supported, patch(
            "src.validator.cli.capture.capture_sheet_png"
        ), patch(
            "src.validator.cli.get_baseline_path"
        ) as mock_baseline_path, patch(
            "src.validator.cli.pixel_diff.diff_png"
        ) as mock_diff:

            mock_supported.return_value = True

            # Mock existing baseline
            mock_baseline = Mock()
            mock_baseline.exists.return_value = True
            mock_baseline_path.return_value = mock_baseline

            # Mock significant visual difference
            mock_diff.return_value = 0.05  # 5% difference

            failures = run_visual_validation(
                mock_workbook, mock_config, workbook_path, "auto", update_baseline=False
            )

            # Should have one failure for visual difference
            assert len(failures) == 1
            assert failures[0].type == "visual_diff"
            assert "5.00%" in failures[0].message

    def test_validation_mode_visual_pass(self, tmp_path):
        """Test validation mode when visual validation passes."""
        # Setup mock workbook and config
        mock_workbook = Mock()
        mock_workbook.sheetnames = ["Sheet1"]
        mock_config = Mock()

        workbook_path = tmp_path / "test.xlsx"
        workbook_path.write_bytes(b"fake xlsx content")

        with patch(
            "src.validator.cli.capture.is_capture_supported"
        ) as mock_supported, patch(
            "src.validator.cli.capture.capture_sheet_png"
        ), patch(
            "src.validator.cli.get_baseline_path"
        ) as mock_baseline_path, patch(
            "src.validator.cli.pixel_diff.diff_png"
        ) as mock_diff:

            mock_supported.return_value = True

            # Mock existing baseline
            mock_baseline = Mock()
            mock_baseline.exists.return_value = True
            mock_baseline_path.return_value = mock_baseline

            # Mock minimal visual difference
            mock_diff.return_value = 0.005  # 0.5% difference (below 1% threshold)

            failures = run_visual_validation(
                mock_workbook, mock_config, workbook_path, "auto", update_baseline=False
            )

            # Should have no failures - validation passed
            assert failures == []

    def test_capture_not_supported(self, tmp_path):
        """Test behavior when screenshot capture is not supported."""
        # Setup mock workbook and config
        mock_workbook = Mock()
        mock_workbook.sheetnames = ["Sheet1"]
        mock_config = Mock()

        workbook_path = tmp_path / "test.xlsx"

        with patch("src.validator.cli.capture.is_capture_supported") as mock_supported:
            mock_supported.return_value = False

            failures = run_visual_validation(
                mock_workbook, mock_config, workbook_path, "auto", update_baseline=False
            )

            # Should return empty list when capture not supported
            assert failures == []

    def test_capture_error_handling(self, tmp_path):
        """Test error handling during screenshot capture."""
        # Setup mock workbook and config
        mock_workbook = Mock()
        mock_workbook.sheetnames = ["Sheet1"]
        mock_config = Mock()

        workbook_path = tmp_path / "test.xlsx"
        workbook_path.write_bytes(b"fake xlsx content")

        with patch(
            "src.validator.cli.capture.is_capture_supported"
        ) as mock_supported, patch(
            "src.validator.cli.capture.capture_sheet_png"
        ) as mock_capture:

            mock_supported.return_value = True
            mock_capture.side_effect = RuntimeError("Screenshot failed")

            failures = run_visual_validation(
                mock_workbook, mock_config, workbook_path, "auto", update_baseline=False
            )

            # Should have one failure for capture error
            assert len(failures) == 1
            assert failures[0].type == "visual_error"
            assert "Screenshot failed" in failures[0].message


class TestGetBaselinePath:
    """Tests for baseline path generation."""

    def test_baseline_path_generation(self):
        """Test correct baseline path generation."""
        path = get_baseline_path("test_workbook", "Sheet1")

        expected = Path("baselines") / "sheets" / "test_workbook" / "Sheet1.png"
        assert path == expected

    def test_baseline_path_special_characters(self):
        """Test baseline path with special characters in names."""
        path = get_baseline_path("my-workbook_v2", "Summary & Analysis")

        expected = (
            Path("baselines") / "sheets" / "my-workbook_v2" / "Summary & Analysis.png"
        )
        assert path == expected


class TestUpdateBaselineFile:
    """Tests for baseline file update functionality."""

    def test_update_baseline_file(self, tmp_path):
        """Test updating a baseline file."""
        # Create source file
        source_path = tmp_path / "source.png"
        source_path.write_bytes(b"fake png content")

        # Define baseline path
        baseline_path = tmp_path / "baselines" / "sheets" / "test" / "Sheet1.png"

        # Update baseline
        update_baseline_file(source_path, baseline_path)

        # Verify baseline was created and has correct content
        assert baseline_path.exists()
        assert baseline_path.read_bytes() == b"fake png content"

    def test_update_baseline_creates_directories(self, tmp_path):
        """Test that update creates necessary directories."""
        # Create source file
        source_path = tmp_path / "source.png"
        source_path.write_bytes(b"fake png content")

        # Define baseline path with non-existent directories
        baseline_path = (
            tmp_path / "new" / "baselines" / "sheets" / "test" / "Sheet1.png"
        )

        # Update baseline
        update_baseline_file(source_path, baseline_path)

        # Verify directories were created
        assert baseline_path.parent.exists()
        assert baseline_path.exists()

    def test_update_baseline_overwrites_existing(self, tmp_path):
        """Test that update overwrites existing baseline files."""
        # Create existing baseline
        baseline_path = tmp_path / "baseline.png"
        baseline_path.write_bytes(b"old content")

        # Create new source file
        source_path = tmp_path / "source.png"
        source_path.write_bytes(b"new content")

        # Update baseline
        update_baseline_file(source_path, baseline_path)

        # Verify baseline was overwritten
        assert baseline_path.read_bytes() == b"new content"


class TestIntegrationScenario:
    """Integration tests following the issue's acceptance criteria."""

    def test_fail_then_pass_scenario(self, tmp_path):
        """Test the scenario: fail on diff, then pass with --update-baseline."""
        # Setup mock workbook and config
        mock_workbook = Mock()
        mock_workbook.sheetnames = ["Sheet1"]
        mock_config = Mock()

        workbook_path = tmp_path / "test.xlsx"
        workbook_path.write_bytes(b"fake xlsx content")

        # Create an existing baseline that will differ from new capture
        baseline_path = tmp_path / "baselines" / "sheets" / "test" / "Sheet1.png"
        baseline_path.parent.mkdir(parents=True, exist_ok=True)
        baseline_path.write_bytes(b"old baseline content")

        with patch(
            "src.validator.cli.capture.is_capture_supported"
        ) as mock_supported, patch(
            "src.validator.cli.capture.capture_sheet_png"
        ), patch(
            "src.validator.cli.pixel_diff.diff_png"
        ) as mock_diff, patch(
            "src.validator.cli.get_baseline_path"
        ) as mock_baseline_path:

            mock_supported.return_value = True
            mock_baseline_path.return_value = baseline_path

            # First run: validation mode with difference
            mock_diff.return_value = 0.05  # 5% difference

            failures_validation = run_visual_validation(
                mock_workbook, mock_config, workbook_path, "auto", update_baseline=False
            )

            # Should fail with visual difference
            assert len(failures_validation) == 1
            assert failures_validation[0].type == "visual_diff"

            # Second run: update baseline mode
            with patch("src.validator.cli.update_baseline_file") as mock_update:
                failures_update = run_visual_validation(
                    mock_workbook,
                    mock_config,
                    workbook_path,
                    "auto",
                    update_baseline=True,
                )

                # Should pass with no failures in update mode
                assert failures_update == []

                # Should have called update_baseline_file
                mock_update.assert_called_once()
