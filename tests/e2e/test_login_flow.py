"""E2E tests for Login flow.

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
class TestLoginFlow:
    """E2E tests for the login flow."""

    def test_login_page_loads(self, page: Page, flet_app: subprocess.Popen):
        """Test that login page loads without errors."""
        base_page = BasePage(page)
        base_page.navigate_to("/login")

        # Verify canvas rendered (Flet app loaded)
        assert base_page.has_canvas(), "Flet canvas should be present"

        # Verify no JavaScript errors
        assert not base_page.has_errors(), f"JS errors: {base_page.get_errors()}"

    def test_login_page_has_title(self, page: Page, flet_app: subprocess.Popen):
        """Test login page has appropriate title."""
        base_page = BasePage(page)
        base_page.navigate_to("/login")

        title = base_page.get_page_title()
        assert title is not None

    def test_login_page_url(self, page: Page, flet_app: subprocess.Popen):
        """Test login page URL is correct."""
        base_page = BasePage(page)
        base_page.navigate_to("/login")

        assert "/login" in base_page.get_url()

    def test_login_page_screenshot(self, page: Page, flet_app: subprocess.Popen):
        """Take screenshot of login page for visual verification."""
        base_page = BasePage(page)
        base_page.navigate_to("/login")
        base_page.wait_for_timeout(1000)  # Wait for animations

        screenshot_path = base_page.take_screenshot("login_page")
        assert screenshot_path.exists(), "Screenshot should be saved"

    def test_login_page_reload(self, page: Page, flet_app: subprocess.Popen):
        """Test login page handles reload correctly."""
        base_page = BasePage(page)
        base_page.navigate_to("/login")

        base_page.reload()

        assert base_page.has_canvas(), "Canvas should be present after reload"
        assert not base_page.has_errors(), "No JS errors after reload"

    def test_login_page_multiple_visits(self, page: Page, flet_app: subprocess.Popen):
        """Test login page can be visited multiple times."""
        base_page = BasePage(page)

        # Visit multiple times
        for _ in range(3):
            base_page.navigate_to("/login")
            base_page.clear_errors()

        assert base_page.has_canvas(), "Canvas should be present"
        assert not base_page.has_errors(), "No accumulated JS errors"
