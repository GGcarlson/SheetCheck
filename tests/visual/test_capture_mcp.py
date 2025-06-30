"""Tests for MCP screenshot capture functionality."""

from unittest.mock import Mock, patch
import pytest

from src.visual import capture_mcp


class TestCaptureSheetPng:
    """Tests for capture_sheet_png function."""

    def test_capture_success(self, tmp_path):
        """Test successful screenshot capture."""
        # Create test files
        wb_path = tmp_path / "test.xlsx"
        wb_path.write_bytes(b"fake xlsx content")
        png_path = tmp_path / "screenshot.png"

        # Mock successful HTML generation
        mock_html = "<html><body>Test Excel Sheet</body></html>"

        with patch(
            "src.visual.capture_mcp._generate_html_from_excel"
        ) as mock_gen, patch(
            "src.visual.capture_mcp._capture_html_screenshot"
        ) as mock_cap, patch(
            "src.visual.capture_mcp.MCP_AVAILABLE", True
        ):

            mock_gen.return_value = mock_html

            # Mock successful screenshot (create actual file)
            def mock_screenshot(html_path, png_path):
                png_path.write_bytes(b"fake png content" * 1000)  # >10KB

            mock_cap.side_effect = mock_screenshot

            # Test the function
            capture_mcp.capture_sheet_png(wb_path, "Sheet1", png_path)

            # Verify calls
            mock_gen.assert_called_once_with(wb_path, "Sheet1")
            mock_cap.assert_called_once()

            # Verify file was created
            assert png_path.exists()
            assert png_path.stat().st_size > 10000

    def test_mcp_not_available(self, tmp_path):
        """Test error when MCP tools are not available."""
        wb_path = tmp_path / "test.xlsx"
        wb_path.write_bytes(b"fake xlsx content")
        png_path = tmp_path / "screenshot.png"

        with patch("src.visual.capture_mcp.MCP_AVAILABLE", False):
            with pytest.raises(
                ImportError, match="MCP Puppeteer tools are not available"
            ):
                capture_mcp.capture_sheet_png(wb_path, "Sheet1", png_path)

    def test_workbook_not_found(self, tmp_path):
        """Test error when workbook file doesn't exist."""
        wb_path = tmp_path / "nonexistent.xlsx"
        png_path = tmp_path / "screenshot.png"

        with patch("src.visual.capture_mcp.MCP_AVAILABLE", True):
            with pytest.raises(FileNotFoundError, match="Workbook file not found"):
                capture_mcp.capture_sheet_png(wb_path, "Sheet1", png_path)

    def test_small_png_file_error(self, tmp_path):
        """Test error when PNG file is too small (corrupted)."""
        wb_path = tmp_path / "test.xlsx"
        wb_path.write_bytes(b"fake xlsx content")
        png_path = tmp_path / "screenshot.png"

        mock_html = "<html><body>Test Excel Sheet</body></html>"

        with patch(
            "src.visual.capture_mcp._generate_html_from_excel"
        ) as mock_gen, patch(
            "src.visual.capture_mcp._capture_html_screenshot"
        ) as mock_cap, patch(
            "src.visual.capture_mcp.MCP_AVAILABLE", True
        ):

            mock_gen.return_value = mock_html

            # Mock screenshot that creates small file
            def mock_screenshot(html_path, png_path):
                png_path.write_bytes(b"small")  # <10KB

            mock_cap.side_effect = mock_screenshot

            with pytest.raises(
                RuntimeError, match="PNG file appears corrupted or too small"
            ):
                capture_mcp.capture_sheet_png(wb_path, "Sheet1", png_path)

    def test_cleanup_on_error(self, tmp_path):
        """Test that temporary files are cleaned up on error."""
        wb_path = tmp_path / "test.xlsx"
        wb_path.write_bytes(b"fake xlsx content")
        png_path = tmp_path / "screenshot.png"

        with patch(
            "src.visual.capture_mcp._generate_html_from_excel"
        ) as mock_gen, patch("src.visual.capture_mcp.MCP_AVAILABLE", True):

            # Mock HTML generation failure
            mock_gen.side_effect = RuntimeError("HTML generation failed")

            with pytest.raises(RuntimeError, match="MCP screenshot capture failed"):
                capture_mcp.capture_sheet_png(wb_path, "Sheet1", png_path)

            # Verify PNG file wasn't left behind
            assert not png_path.exists()


class TestGenerateHtmlFromExcel:
    """Tests for HTML generation from Excel."""

    def test_successful_html_generation(self, tmp_path):
        """Test successful HTML generation."""
        wb_path = tmp_path / "test.xlsx"
        wb_path.write_bytes(b"fake xlsx content")

        mock_html = "<html><body><table>Excel Content</table></body></html>"

        with patch("subprocess.run") as mock_run, patch(
            "src.visual.capture_mcp.Path"
        ) as mock_path:

            # Mock successful subprocess call
            mock_result = Mock()
            mock_result.returncode = 0
            mock_result.stdout = mock_html
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            # Mock path resolution - create mock script path that exists
            mock_script = Mock()
            mock_script.exists.return_value = True

            # Mock the Path() call chain
            mock_path_obj = Mock()
            mock_path_obj.parent.parent.parent.__truediv__.return_value.__truediv__.return_value = (
                mock_script
            )
            mock_path.return_value = mock_path_obj

            result = capture_mcp._generate_html_from_excel(wb_path, "Sheet1")

            assert result == mock_html
            mock_run.assert_called_once()

    def test_render_script_not_found(self, tmp_path):
        """Test error when Node.js helper script is missing."""
        wb_path = tmp_path / "test.xlsx"

        with patch("src.visual.capture_mcp.Path") as mock_path_class:
            # Mock script path that doesn't exist
            mock_script_path = Mock()
            mock_script_path.exists.return_value = False
            mock_path_class.return_value.parent.parent.parent = Mock()
            mock_path_class.return_value.parent.parent.parent.__truediv__ = (
                lambda self, x: mock_script_path
            )

            with pytest.raises(
                FileNotFoundError, match="Node.js helper script not found"
            ):
                capture_mcp._generate_html_from_excel(wb_path, "Sheet1")

    def test_sheet_not_found_error(self, tmp_path):
        """Test error when sheet name doesn't exist."""
        wb_path = tmp_path / "test.xlsx"

        with patch("subprocess.run") as mock_run, patch.object(
            capture_mcp, "Path"
        ) as mock_path_class:

            # Mock error result for sheet not found
            mock_result = Mock()
            mock_result.returncode = 1
            mock_result.stdout = ""
            mock_result.stderr = "Error: Sheet 'BadSheet' not found in workbook"
            mock_run.return_value = mock_result

            # Mock script path exists
            mock_script_path = Mock()
            mock_script_path.exists.return_value = True
            mock_path_class.return_value.parent.parent.parent = Mock()
            mock_path_class.return_value.parent.parent.parent.__truediv__ = (
                lambda self, x: mock_script_path
            )

            with pytest.raises(ValueError, match="Sheet 'BadSheet' not found"):
                capture_mcp._generate_html_from_excel(wb_path, "BadSheet")

    def test_nodejs_not_found(self, tmp_path):
        """Test error when Node.js is not installed."""
        wb_path = tmp_path / "test.xlsx"

        with patch("subprocess.run") as mock_run, patch.object(
            capture_mcp, "Path"
        ) as mock_path_class:

            # Mock Node.js not found error
            mock_run.side_effect = FileNotFoundError("node not found")

            # Mock script path exists
            mock_script_path = Mock()
            mock_script_path.exists.return_value = True
            mock_path_class.return_value.parent.parent.parent = Mock()
            mock_path_class.return_value.parent.parent.parent.__truediv__ = (
                lambda self, x: mock_script_path
            )

            with pytest.raises(FileNotFoundError, match="Node.js not found"):
                capture_mcp._generate_html_from_excel(wb_path, "Sheet1")

    def test_timeout_error(self, tmp_path):
        """Test timeout during HTML generation."""
        wb_path = tmp_path / "test.xlsx"

        with patch("subprocess.run") as mock_run, patch.object(
            capture_mcp, "Path"
        ) as mock_path_class:

            # Mock timeout
            from subprocess import TimeoutExpired

            mock_run.side_effect = TimeoutExpired("node", 30)

            # Mock script path exists
            mock_script_path = Mock()
            mock_script_path.exists.return_value = True
            mock_path_class.return_value.parent.parent.parent = Mock()
            mock_path_class.return_value.parent.parent.parent.__truediv__ = (
                lambda self, x: mock_script_path
            )

            with pytest.raises(RuntimeError, match="HTML generation timed out"):
                capture_mcp._generate_html_from_excel(wb_path, "Sheet1")


class TestCaptureHtmlScreenshot:
    """Tests for Puppeteer MCP screenshot capture."""

    def test_successful_screenshot(self, tmp_path):
        """Test successful screenshot capture."""
        html_path = tmp_path / "test.html"
        html_path.write_text("<html><body>Test</body></html>")
        png_path = tmp_path / "screenshot.png"

        with patch.object(
            capture_mcp, "mcp__puppeteer__navigate"
        ) as mock_nav, patch.object(
            capture_mcp, "mcp__puppeteer__screenshot"
        ) as mock_screen:

            # Mock successful MCP calls
            mock_nav.return_value = {"success": True}
            mock_screen.return_value = {"success": True}

            capture_mcp._capture_html_screenshot(html_path, png_path)

            # Verify MCP calls
            mock_nav.assert_called_once()
            mock_screen.assert_called_once()

            # Check screenshot options
            call_args = mock_screen.call_args[0][0]
            assert call_args["path"] == str(png_path)
            assert call_args["fullPage"] is True
            assert call_args["type"] == "png"

    def test_navigation_failure(self, tmp_path):
        """Test error when navigation fails."""
        html_path = tmp_path / "test.html"
        png_path = tmp_path / "screenshot.png"

        with patch.object(capture_mcp, "mcp__puppeteer__navigate") as mock_nav:
            # Mock navigation failure
            mock_nav.return_value = {"error": "Navigation failed"}

            with pytest.raises(RuntimeError, match="Failed to navigate to HTML file"):
                capture_mcp._capture_html_screenshot(html_path, png_path)

    def test_screenshot_failure(self, tmp_path):
        """Test error when screenshot fails."""
        html_path = tmp_path / "test.html"
        png_path = tmp_path / "screenshot.png"

        with patch.object(
            capture_mcp, "mcp__puppeteer__navigate"
        ) as mock_nav, patch.object(
            capture_mcp, "mcp__puppeteer__screenshot"
        ) as mock_screen:

            # Mock successful navigation but failed screenshot
            mock_nav.return_value = {"success": True}
            mock_screen.return_value = {"error": "Screenshot failed"}

            with pytest.raises(RuntimeError, match="Failed to capture screenshot"):
                capture_mcp._capture_html_screenshot(html_path, png_path)


class TestMcpSuccessCheck:
    """Tests for MCP result success checking."""

    def test_dict_success_true(self):
        """Test success detection with dict containing success=True."""
        result = {"success": True, "data": "screenshot saved"}
        assert capture_mcp._is_mcp_success(result) is True

    def test_dict_error_present(self):
        """Test failure detection with dict containing error."""
        result = {"error": "Navigation failed", "code": 500}
        assert capture_mcp._is_mcp_success(result) is False

    def test_dict_no_error_field(self):
        """Test success detection with dict without error field."""
        result = {"status": "ok", "timestamp": "2024-01-01"}
        assert capture_mcp._is_mcp_success(result) is True

    def test_string_success(self):
        """Test success detection with success string."""
        result = "Screenshot captured successfully"
        assert capture_mcp._is_mcp_success(result) is True

    def test_string_error(self):
        """Test error detection with error string."""
        result = "Error: Failed to load page"
        assert capture_mcp._is_mcp_success(result) is False

    def test_none_result(self):
        """Test handling of None result."""
        assert capture_mcp._is_mcp_success(None) is False

    def test_other_types(self):
        """Test handling of other result types."""
        assert capture_mcp._is_mcp_success(123) is True
        assert capture_mcp._is_mcp_success([1, 2, 3]) is True


class TestSupportAndInfo:
    """Tests for support checking and renderer info."""

    def test_is_capture_supported_true(self):
        """Test support detection when MCP is available."""
        with patch("src.visual.capture_mcp.MCP_AVAILABLE", True):
            assert capture_mcp.is_capture_supported() is True

    def test_is_capture_supported_false(self):
        """Test support detection when MCP is not available."""
        with patch("src.visual.capture_mcp.MCP_AVAILABLE", False):
            assert capture_mcp.is_capture_supported() is False

    @patch("platform.system")
    def test_get_renderer_info_linux_mcp(self, mock_platform):
        """Test renderer info on Linux with MCP available."""
        mock_platform.return_value = "Linux"

        with patch("src.visual.capture_mcp.MCP_AVAILABLE", True):
            info = capture_mcp.get_renderer_info()

            assert info["platform"] == "Linux"
            assert info["mcp_available"] is True
            assert info["preferred_renderer"] == "mcp"

    @patch("platform.system")
    def test_get_renderer_info_windows_with_com(self, mock_platform):
        """Test renderer info on Windows with COM available."""
        mock_platform.return_value = "Windows"

        with patch.object(capture_mcp, "MCP_AVAILABLE", True), patch(
            "src.visual.capture_mcp.capture_com", create=True
        ) as mock_com:

            mock_com.is_capture_supported.return_value = True

            info = capture_mcp.get_renderer_info()

            assert info["platform"] == "Windows"
            assert info["mcp_available"] is True
            assert info["com_available"] is True
            assert info["preferred_renderer"] == "mcp"  # MCP module doesn't prefer COM
