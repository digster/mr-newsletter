"""E2E tests for Settings page.

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
class TestSettings:
    """E2E tests for the settings page."""

    def test_settings_page_loads(self, page: Page, flet_app: subprocess.Popen):
        """Test that settings page loads without errors."""
        base_page = BasePage(page)
        base_page.navigate_to("/settings")

        # Verify canvas rendered (Flet app loaded)
        assert base_page.has_canvas(), "Flet canvas should be present"

        # Verify no JavaScript errors
        assert not base_page.has_errors(), f"JS errors: {base_page.get_errors()}"

    def test_settings_page_url(self, page: Page, flet_app: subprocess.Popen):
        """Test settings page URL is correct."""
        base_page = BasePage(page)
        base_page.navigate_to("/settings")

        assert "/settings" in base_page.get_url()

    def test_settings_page_screenshot(self, page: Page, flet_app: subprocess.Popen):
        """Take screenshot of settings page for visual verification."""
        base_page = BasePage(page)
        base_page.navigate_to("/settings")
        base_page.wait_for_timeout(1000)  # Wait for animations

        screenshot_path = base_page.take_screenshot("settings_page")
        assert screenshot_path.exists(), "Screenshot should be saved"

    def test_settings_page_reload(self, page: Page, flet_app: subprocess.Popen):
        """Test settings page handles reload correctly."""
        base_page = BasePage(page)
        base_page.navigate_to("/settings")

        base_page.reload()

        assert base_page.has_canvas(), "Canvas should be present after reload"
        assert not base_page.has_errors(), "No JS errors after reload"

    def test_settings_page_title(self, page: Page, flet_app: subprocess.Popen):
        """Test settings page has a title."""
        base_page = BasePage(page)
        base_page.navigate_to("/settings")

        title = base_page.get_page_title()
        assert title is not None

    def test_settings_page_canvas_count(self, page: Page, flet_app: subprocess.Popen):
        """Test settings page has expected canvas elements."""
        base_page = BasePage(page)
        base_page.navigate_to("/settings")

        canvas_count = base_page.get_canvas_count()
        assert canvas_count >= 1, "Should have at least one canvas"
