"""Base Page Object for E2E tests."""

import os
from pathlib import Path
from typing import Optional

from playwright.sync_api import Page, expect

# Test configuration - use host.docker.internal when running in VNC container
USE_VNC_BROWSER = os.environ.get("USE_VNC_BROWSER", "true").lower() == "true"
TEST_HOST = os.environ.get("APP_HOST", "host.docker.internal" if USE_VNC_BROWSER else "127.0.0.1")
TEST_PORT = os.environ.get("APP_PORT", "8550")
TEST_BASE_URL = f"http://{TEST_HOST}:{TEST_PORT}"
SCREENSHOT_DIR = Path(__file__).parent.parent / "screenshots"


class BasePage:
    """Base class for all Page Objects.

    Since Flet renders to HTML Canvas, we cannot interact with
    individual UI elements directly. Instead, we focus on:
    - Page navigation
    - Screenshot comparison
    - JavaScript error detection
    - Basic canvas rendering verification
    """

    def __init__(self, page: Page):
        """Initialize the base page.

        Args:
            page: Playwright Page object.
        """
        self.page = page
        self.base_url = TEST_BASE_URL
        self.errors: list[str] = []

        # Set up error listener
        self.page.on("pageerror", lambda err: self.errors.append(str(err)))

    def navigate_to(self, path: str = "") -> None:
        """Navigate to a specific path.

        Args:
            path: URL path (without base).
        """
        self.page.goto(f"{self.base_url}{path}")
        self.wait_for_load()

    def wait_for_load(self, timeout: int = 10000) -> None:
        """Wait for Flet app to fully load.

        Args:
            timeout: Maximum wait time in milliseconds.
        """
        self.page.wait_for_load_state("networkidle")
        # Wait for Flet canvas to render
        self.page.wait_for_selector("canvas", timeout=timeout)

    def take_screenshot(self, name: str) -> Path:
        """Take a screenshot for debugging.

        Args:
            name: Screenshot name (without extension).

        Returns:
            Path to the screenshot file.
        """
        SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
        screenshot_path = SCREENSHOT_DIR / f"{name}.png"
        self.page.screenshot(path=screenshot_path)
        return screenshot_path

    def has_canvas(self) -> bool:
        """Check if Flet canvas is present.

        Returns:
            True if canvas element exists.
        """
        canvas = self.page.locator("canvas")
        return canvas.count() > 0

    def get_canvas_count(self) -> int:
        """Get number of canvas elements.

        Returns:
            Number of canvas elements.
        """
        return self.page.locator("canvas").count()

    def has_errors(self) -> bool:
        """Check if any JavaScript errors occurred.

        Returns:
            True if errors were captured.
        """
        return len(self.errors) > 0

    def get_errors(self) -> list[str]:
        """Get captured JavaScript errors.

        Returns:
            List of error messages.
        """
        return self.errors.copy()

    def clear_errors(self) -> None:
        """Clear captured errors."""
        self.errors.clear()

    def wait_for_timeout(self, timeout: int) -> None:
        """Wait for specified timeout.

        Args:
            timeout: Wait time in milliseconds.
        """
        self.page.wait_for_timeout(timeout)

    def get_page_title(self) -> str:
        """Get the page title.

        Returns:
            Page title string.
        """
        return self.page.title()

    def get_url(self) -> str:
        """Get current URL.

        Returns:
            Current page URL.
        """
        return self.page.url

    def reload(self) -> None:
        """Reload the current page."""
        self.page.reload()
        self.wait_for_load()
