"""E2E tests for Email Reader page.

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
class TestEmailReader:
    """E2E tests for the email reader page."""

    def test_email_reader_page_loads(self, page: Page, flet_app: subprocess.Popen):
        """Test that email reader page loads without errors."""
        base_page = BasePage(page)
        # Navigate to email with ID 1
        base_page.navigate_to("/email/1")

        # Verify canvas rendered (Flet app loaded)
        assert base_page.has_canvas(), "Flet canvas should be present"

        # Verify no JavaScript errors
        assert not base_page.has_errors(), f"JS errors: {base_page.get_errors()}"

    def test_email_reader_page_url_with_id(self, page: Page, flet_app: subprocess.Popen):
        """Test email reader page URL includes email ID."""
        base_page = BasePage(page)
        base_page.navigate_to("/email/99")

        assert "/email/99" in base_page.get_url()

    def test_email_reader_page_screenshot(self, page: Page, flet_app: subprocess.Popen):
        """Take screenshot of email reader page for visual verification."""
        base_page = BasePage(page)
        base_page.navigate_to("/email/1")
        base_page.wait_for_timeout(1000)  # Wait for animations

        screenshot_path = base_page.take_screenshot("email_reader_page")
        assert screenshot_path.exists(), "Screenshot should be saved"

    def test_email_reader_page_reload(self, page: Page, flet_app: subprocess.Popen):
        """Test email reader page handles reload correctly."""
        base_page = BasePage(page)
        base_page.navigate_to("/email/1")

        base_page.reload()

        assert base_page.has_canvas(), "Canvas should be present after reload"
        assert not base_page.has_errors(), "No JS errors after reload"

    def test_email_reader_different_ids(self, page: Page, flet_app: subprocess.Popen):
        """Test email reader works with different email IDs."""
        base_page = BasePage(page)

        for email_id in [1, 5, 10]:
            base_page.navigate_to(f"/email/{email_id}")
            base_page.clear_errors()
            assert base_page.has_canvas(), f"Canvas should load for email ID {email_id}"

    def test_email_reader_page_title(self, page: Page, flet_app: subprocess.Popen):
        """Test email reader page has a title."""
        base_page = BasePage(page)
        base_page.navigate_to("/email/1")

        title = base_page.get_page_title()
        assert title is not None
