"""Tests for unified capture interface with automatic renderer selection."""

from unittest.mock import patch
import pytest

from src.visual import capture


class TestCaptureSheetPng:
    """Tests for unified capture_sheet_png function."""

    def test_auto_renderer_windows_com(self, tmp_path):
        """Test auto renderer selection on Windows with COM available."""
        wb_path = tmp_path / "test.xlsx"
        wb_path.write_bytes(b"fake xlsx content")
        png_path = tmp_path / "screenshot.png"

        mock_info = {
            "platform": "Windows",
            "com_available": True,
            "mcp_available": False,
            "preferred_renderer": "com",
        }

        with patch("src.visual.capture.get_renderer_info") as mock_info_func, patch(
            "src.visual.capture_com.capture_sheet_png"
        ) as mock_capture_com:

            mock_info_func.return_value = mock_info

            capture.capture_sheet_png(wb_path, "Sheet1", png_path, renderer="auto")

            mock_capture_com.assert_called_once_with(
                wb_path, "Sheet1", png_path
            )

    def test_auto_renderer_linux_mcp(self, tmp_path):
        """Test auto renderer selection on Linux with MCP available."""
        wb_path = tmp_path / "test.xlsx"
        wb_path.write_bytes(b"fake xlsx content")
        png_path = tmp_path / "screenshot.png"

        mock_info = {
            "platform": "Linux",
            "com_available": False,
            "mcp_available": True,
            "preferred_renderer": "mcp",
        }

        with patch("src.visual.capture.get_renderer_info") as mock_info_func, patch(
            "src.visual.capture_mcp.capture_sheet_png"
        ) as mock_capture_mcp:

            mock_info_func.return_value = mock_info

            capture.capture_sheet_png(wb_path, "Sheet1", png_path, renderer="auto")

            mock_capture_mcp.assert_called_once_with(
                wb_path, "Sheet1", png_path
            )

    def test_explicit_com_renderer(self, tmp_path):
        """Test explicit COM renderer selection."""
        wb_path = tmp_path / "test.xlsx"
        png_path = tmp_path / "screenshot.png"

        mock_info = {"com_available": True, "mcp_available": True}

        with patch("src.visual.capture.get_renderer_info") as mock_info_func, patch(
            "src.visual.capture_com.capture_sheet_png"
        ) as mock_capture_com:

            mock_info_func.return_value = mock_info

            capture.capture_sheet_png(wb_path, "Sheet1", png_path, renderer="com")

            mock_capture_com.assert_called_once_with(
                wb_path, "Sheet1", png_path
            )

    def test_explicit_mcp_renderer(self, tmp_path):
        """Test explicit MCP renderer selection."""
        wb_path = tmp_path / "test.xlsx"
        png_path = tmp_path / "screenshot.png"

        mock_info = {"com_available": True, "mcp_available": True}

        with patch("src.visual.capture.get_renderer_info") as mock_info_func, patch(
            "src.visual.capture_mcp.capture_sheet_png"
        ) as mock_capture_mcp:

            mock_info_func.return_value = mock_info

            capture.capture_sheet_png(wb_path, "Sheet1", png_path, renderer="mcp")

            mock_capture_mcp.assert_called_once_with(
                wb_path, "Sheet1", png_path
            )

    def test_com_not_available_error(self, tmp_path):
        """Test error when requesting COM but not available."""
        wb_path = tmp_path / "test.xlsx"
        png_path = tmp_path / "screenshot.png"

        mock_info = {"com_available": False, "mcp_available": True}

        with patch("src.visual.capture.get_renderer_info") as mock_info_func:
            mock_info_func.return_value = mock_info

            with pytest.raises(ImportError, match="COM renderer not available"):
                capture.capture_sheet_png(wb_path, "Sheet1", png_path, renderer="com")

    def test_mcp_not_available_error(self, tmp_path):
        """Test error when requesting MCP but not available."""
        wb_path = tmp_path / "test.xlsx"
        png_path = tmp_path / "screenshot.png"

        mock_info = {"com_available": True, "mcp_available": False}

        with patch("src.visual.capture.get_renderer_info") as mock_info_func:
            mock_info_func.return_value = mock_info

            with pytest.raises(ImportError, match="MCP renderer not available"):
                capture.capture_sheet_png(wb_path, "Sheet1", png_path, renderer="mcp")

    def test_no_renderers_available(self, tmp_path):
        """Test error when no renderers are available."""
        wb_path = tmp_path / "test.xlsx"
        png_path = tmp_path / "screenshot.png"

        mock_info = {
            "com_available": False,
            "mcp_available": False,
            "preferred_renderer": "none",
        }

        with patch("src.visual.capture.get_renderer_info") as mock_info_func:
            mock_info_func.return_value = mock_info

            with pytest.raises(ImportError, match="No screenshot renderers available"):
                capture.capture_sheet_png(wb_path, "Sheet1", png_path, renderer="auto")

    def test_invalid_renderer(self, tmp_path):
        """Test error with invalid renderer name."""
        wb_path = tmp_path / "test.xlsx"
        png_path = tmp_path / "screenshot.png"

        mock_info = {"com_available": True, "mcp_available": True}

        with patch("src.visual.capture.get_renderer_info") as mock_info_func:
            mock_info_func.return_value = mock_info

            with pytest.raises(ValueError, match="Invalid renderer 'invalid'"):
                capture.capture_sheet_png(
                    wb_path, "Sheet1", png_path, renderer="invalid"
                )


class TestGetRendererInfo:
    """Tests for get_renderer_info function."""

    @patch("platform.system")
    def test_windows_with_com_available(self, mock_platform):
        """Test renderer info on Windows with COM available."""
        mock_platform.return_value = "Windows"

        with patch("src.visual.capture_com.is_capture_supported") as mock_com_supported:
            mock_com_supported.return_value = True

            with patch("src.visual.capture_mcp.is_capture_supported") as mock_mcp_supported:
                mock_mcp_supported.return_value = False

                info = capture.get_renderer_info()

                assert info["platform"] == "Windows"
                assert info["com_available"] is True
                assert info["mcp_available"] is False
                assert info["preferred_renderer"] == "com"

    @patch("platform.system")
    def test_linux_with_mcp_available(self, mock_platform):
        """Test renderer info on Linux with MCP available."""
        mock_platform.return_value = "Linux"

        with patch("src.visual.capture_mcp.is_capture_supported") as mock_mcp_supported:
            mock_mcp_supported.return_value = True

            info = capture.get_renderer_info()

            assert info["platform"] == "Linux"
            assert info["com_available"] is False
            assert info["mcp_available"] is True
            assert info["preferred_renderer"] == "mcp"

    @patch("platform.system")
    def test_windows_with_both_available(self, mock_platform):
        """Test renderer info on Windows with both renderers available."""
        mock_platform.return_value = "Windows"

        with patch("src.visual.capture_com.is_capture_supported") as mock_com_supported, patch(
            "src.visual.capture_mcp.is_capture_supported"
        ) as mock_mcp_supported:

            mock_com_supported.return_value = True
            mock_mcp_supported.return_value = True

            info = capture.get_renderer_info()

            assert info["platform"] == "Windows"
            assert info["com_available"] is True
            assert info["mcp_available"] is True
            assert info["preferred_renderer"] == "com"  # COM preferred on Windows

    @patch("platform.system")
    def test_no_renderers_available(self, mock_platform):
        """Test renderer info when no renderers available."""
        mock_platform.return_value = "Linux"

        with patch("src.visual.capture_mcp.is_capture_supported") as mock_mcp_supported:
            mock_mcp_supported.return_value = False

            info = capture.get_renderer_info()

            assert info["platform"] == "Linux"
            assert info["com_available"] is False
            assert info["mcp_available"] is False
            assert info["preferred_renderer"] == "none"

    @patch("platform.system")
    def test_import_errors_handled(self, mock_platform):
        """Test that import errors are handled gracefully."""
        mock_platform.return_value = "Windows"

        # Mock import errors for both modules
        with patch("src.visual.capture_com", side_effect=ImportError), patch(
            "src.visual.capture_mcp", side_effect=ImportError
        ):

            info = capture.get_renderer_info()

            assert info["platform"] == "Windows"
            assert info["com_available"] is False
            assert info["mcp_available"] is False
            assert info["preferred_renderer"] == "none"


class TestIsCaptureSupported:
    """Tests for is_capture_supported function."""

    def test_com_available(self):
        """Test support detection when COM is available."""
        mock_info = {"com_available": True, "mcp_available": False}

        with patch("src.visual.capture.get_renderer_info") as mock_info_func:
            mock_info_func.return_value = mock_info

            assert capture.is_capture_supported() is True

    def test_mcp_available(self):
        """Test support detection when MCP is available."""
        mock_info = {"com_available": False, "mcp_available": True}

        with patch("src.visual.capture.get_renderer_info") as mock_info_func:
            mock_info_func.return_value = mock_info

            assert capture.is_capture_supported() is True

    def test_both_available(self):
        """Test support detection when both renderers are available."""
        mock_info = {"com_available": True, "mcp_available": True}

        with patch("src.visual.capture.get_renderer_info") as mock_info_func:
            mock_info_func.return_value = mock_info

            assert capture.is_capture_supported() is True

    def test_none_available(self):
        """Test support detection when no renderers are available."""
        mock_info = {"com_available": False, "mcp_available": False}

        with patch("src.visual.capture.get_renderer_info") as mock_info_func:
            mock_info_func.return_value = mock_info

            assert capture.is_capture_supported() is False
