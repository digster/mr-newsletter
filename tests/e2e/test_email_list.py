"""E2E tests for Email List page.

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
class TestEmailList:
    """E2E tests for the email list page."""

    def test_email_list_page_loads(self, page: Page, flet_app: subprocess.Popen):
        """Test that email list page loads without errors."""
        base_page = BasePage(page)
        # Navigate to newsletter with ID 1
        base_page.navigate_to("/newsletter/1")

        # Verify canvas rendered (Flet app loaded)
        assert base_page.has_canvas(), "Flet canvas should be present"

        # Verify no JavaScript errors
        assert not base_page.has_errors(), f"JS errors: {base_page.get_errors()}"

    def test_email_list_page_url_with_id(self, page: Page, flet_app: subprocess.Popen):
        """Test email list page URL includes newsletter ID."""
        base_page = BasePage(page)
        base_page.navigate_to("/newsletter/42")

        assert "/newsletter/42" in base_page.get_url()

    def test_email_list_page_screenshot(self, page: Page, flet_app: subprocess.Popen):
        """Take screenshot of email list page for visual verification."""
        base_page = BasePage(page)
        base_page.navigate_to("/newsletter/1")
        base_page.wait_for_timeout(1000)  # Wait for animations

        screenshot_path = base_page.take_screenshot("email_list_page")
        assert screenshot_path.exists(), "Screenshot should be saved"

    def test_email_list_page_reload(self, page: Page, flet_app: subprocess.Popen):
        """Test email list page handles reload correctly."""
        base_page = BasePage(page)
        base_page.navigate_to("/newsletter/1")

        base_page.reload()

        assert base_page.has_canvas(), "Canvas should be present after reload"
        assert not base_page.has_errors(), "No JS errors after reload"

    def test_email_list_different_ids(self, page: Page, flet_app: subprocess.Popen):
        """Test email list works with different newsletter IDs."""
        base_page = BasePage(page)

        for newsletter_id in [1, 2, 3]:
            base_page.navigate_to(f"/newsletter/{newsletter_id}")
            base_page.clear_errors()
            assert base_page.has_canvas(), f"Canvas should load for ID {newsletter_id}"
