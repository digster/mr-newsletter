"""E2E tests for Navigation between pages.

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
class TestNavigation:
    """E2E tests for navigation between pages."""

    def test_navigate_to_all_main_pages(self, page: Page, flet_app: subprocess.Popen):
        """Test navigation to all main pages works."""
        base_page = BasePage(page)

        pages_to_test = [
            "/home",
            "/newsletters",
            "/settings",
            "/login",
            "/setup",
        ]

        for page_path in pages_to_test:
            base_page.navigate_to(page_path)
            base_page.clear_errors()

            assert base_page.has_canvas(), f"Canvas should load for {page_path}"
            assert not base_page.has_errors(), f"No JS errors for {page_path}"

    def test_navigate_home_to_settings(self, page: Page, flet_app: subprocess.Popen):
        """Test navigation from home to settings."""
        base_page = BasePage(page)

        base_page.navigate_to("/home")
        assert base_page.has_canvas()

        base_page.navigate_to("/settings")
        assert "/settings" in base_page.get_url()
        assert base_page.has_canvas()

    def test_navigate_home_to_newsletters(self, page: Page, flet_app: subprocess.Popen):
        """Test navigation from home to newsletters."""
        base_page = BasePage(page)

        base_page.navigate_to("/home")
        assert base_page.has_canvas()

        base_page.navigate_to("/newsletters")
        assert "/newsletters" in base_page.get_url()
        assert base_page.has_canvas()

    def test_navigate_to_email_list(self, page: Page, flet_app: subprocess.Popen):
        """Test navigation to email list with newsletter ID."""
        base_page = BasePage(page)

        base_page.navigate_to("/home")
        base_page.navigate_to("/newsletter/1")

        assert "/newsletter/1" in base_page.get_url()
        assert base_page.has_canvas()

    def test_navigate_to_email_reader(self, page: Page, flet_app: subprocess.Popen):
        """Test navigation to email reader with email ID."""
        base_page = BasePage(page)

        base_page.navigate_to("/newsletter/1")
        base_page.navigate_to("/email/1")

        assert "/email/1" in base_page.get_url()
        assert base_page.has_canvas()

    def test_deep_navigation_path(self, page: Page, flet_app: subprocess.Popen):
        """Test deep navigation path: home -> newsletter -> email."""
        base_page = BasePage(page)

        # Navigate through the app
        base_page.navigate_to("/home")
        assert base_page.has_canvas()

        base_page.navigate_to("/newsletter/1")
        assert base_page.has_canvas()

        base_page.navigate_to("/email/1")
        assert base_page.has_canvas()

        # Navigate back to home
        base_page.navigate_to("/home")
        assert "/home" in base_page.get_url()

    def test_no_errors_during_navigation(self, page: Page, flet_app: subprocess.Popen):
        """Test no JavaScript errors accumulate during navigation."""
        base_page = BasePage(page)

        pages = ["/home", "/newsletters", "/settings", "/home"]

        for page_path in pages:
            base_page.navigate_to(page_path)

        # Check no errors accumulated
        assert not base_page.has_errors(), f"Accumulated errors: {base_page.get_errors()}"

    def test_rapid_navigation(self, page: Page, flet_app: subprocess.Popen):
        """Test rapid navigation between pages."""
        base_page = BasePage(page)

        # Rapid navigation
        for _ in range(5):
            base_page.page.goto(f"{TEST_BASE_URL}/home")
            base_page.page.goto(f"{TEST_BASE_URL}/settings")

        # Wait for final page to load
        base_page.wait_for_load()

        assert base_page.has_canvas(), "Canvas should be present after rapid navigation"

    def test_invalid_route_handling(self, page: Page, flet_app: subprocess.Popen):
        """Test app handles invalid routes gracefully."""
        base_page = BasePage(page)

        # Navigate to invalid route
        base_page.page.goto(f"{TEST_BASE_URL}/invalid-route-12345")

        # App should still render (Flet handles routing)
        # May redirect to home or show error page
        base_page.wait_for_timeout(2000)

        # Canvas should still be present (app didn't crash)
        assert base_page.has_canvas(), "App should handle invalid routes gracefully"

    def test_navigation_preserves_canvas(self, page: Page, flet_app: subprocess.Popen):
        """Test navigation doesn't cause canvas count issues."""
        base_page = BasePage(page)

        base_page.navigate_to("/home")
        initial_count = base_page.get_canvas_count()

        base_page.navigate_to("/settings")
        base_page.navigate_to("/home")

        final_count = base_page.get_canvas_count()
        assert final_count == initial_count, "Canvas count should be consistent"
