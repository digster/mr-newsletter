"""E2E tests for Newsletter Management.

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
class TestNewsletterManagement:
    """E2E tests for newsletter management page."""

    def test_newsletters_page_loads(self, page: Page, flet_app: subprocess.Popen):
        """Test that newsletters page loads without errors."""
        base_page = BasePage(page)
        base_page.navigate_to("/newsletters")

        # Verify canvas rendered (Flet app loaded)
        assert base_page.has_canvas(), "Flet canvas should be present"

        # Verify no JavaScript errors
        assert not base_page.has_errors(), f"JS errors: {base_page.get_errors()}"

    def test_newsletters_page_url(self, page: Page, flet_app: subprocess.Popen):
        """Test newsletters page URL is correct."""
        base_page = BasePage(page)
        base_page.navigate_to("/newsletters")

        assert "/newsletters" in base_page.get_url()

    def test_newsletters_page_screenshot(self, page: Page, flet_app: subprocess.Popen):
        """Take screenshot of newsletters page for visual verification."""
        base_page = BasePage(page)
        base_page.navigate_to("/newsletters")
        base_page.wait_for_timeout(1000)  # Wait for animations

        screenshot_path = base_page.take_screenshot("newsletters_page")
        assert screenshot_path.exists(), "Screenshot should be saved"

    def test_newsletters_page_reload(self, page: Page, flet_app: subprocess.Popen):
        """Test newsletters page handles reload correctly."""
        base_page = BasePage(page)
        base_page.navigate_to("/newsletters")

        base_page.reload()

        assert base_page.has_canvas(), "Canvas should be present after reload"
        assert not base_page.has_errors(), "No JS errors after reload"

    def test_newsletters_page_title(self, page: Page, flet_app: subprocess.Popen):
        """Test newsletters page has a title."""
        base_page = BasePage(page)
        base_page.navigate_to("/newsletters")

        title = base_page.get_page_title()
        assert title is not None
