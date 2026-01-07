"""E2E tests for Home Dashboard.

Since Flet renders to HTML Canvas, these tests focus on:
- Page loading and navigation
- Canvas rendering verification
- JavaScript error detection
- Screenshot capture for visual verification
"""

import subprocess

import pytest
from playwright.sync_api import Page, expect

from tests.e2e.page_objects.base_page import BasePage, TEST_BASE_URL


@pytest.mark.e2e
class TestHomeDashboard:
    """E2E tests for the home dashboard."""

    def test_home_page_loads(self, page: Page, flet_app: subprocess.Popen):
        """Test that home page loads without errors."""
        base_page = BasePage(page)
        base_page.navigate_to("/home")

        # Verify canvas rendered (Flet app loaded)
        assert base_page.has_canvas(), "Flet canvas should be present"

        # Verify no JavaScript errors
        assert not base_page.has_errors(), f"JS errors: {base_page.get_errors()}"

    def test_home_page_url(self, page: Page, flet_app: subprocess.Popen):
        """Test home page URL is correct."""
        base_page = BasePage(page)
        base_page.navigate_to("/home")

        assert "/home" in base_page.get_url()

    def test_home_page_screenshot(self, page: Page, flet_app: subprocess.Popen):
        """Take screenshot of home page for visual verification."""
        base_page = BasePage(page)
        base_page.navigate_to("/home")
        base_page.wait_for_timeout(1000)  # Wait for animations

        screenshot_path = base_page.take_screenshot("home_page")
        assert screenshot_path.exists(), "Screenshot should be saved"

    def test_home_page_reload(self, page: Page, flet_app: subprocess.Popen):
        """Test home page handles reload correctly."""
        base_page = BasePage(page)
        base_page.navigate_to("/home")

        base_page.reload()

        assert base_page.has_canvas(), "Canvas should be present after reload"
        assert not base_page.has_errors(), "No JS errors after reload"

    def test_root_url_redirect(self, page: Page, flet_app: subprocess.Popen):
        """Test root URL loads the app."""
        base_page = BasePage(page)
        base_page.navigate_to("")

        # App should load at root
        assert base_page.has_canvas(), "Flet canvas should be present at root"

    def test_home_page_canvas_stability(self, page: Page, flet_app: subprocess.Popen):
        """Test home page canvas remains stable."""
        base_page = BasePage(page)
        base_page.navigate_to("/home")

        initial_count = base_page.get_canvas_count()
        base_page.wait_for_timeout(2000)
        final_count = base_page.get_canvas_count()

        assert initial_count == final_count, "Canvas count should remain stable"
