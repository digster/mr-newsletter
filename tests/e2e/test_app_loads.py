"""Basic E2E tests to verify the app loads correctly."""

from pathlib import Path

from playwright.sync_api import Page

SCREENSHOT_DIR = Path(__file__).parent / "screenshots"


def test_app_loads_without_errors(app_page: Page) -> None:
    """Test that the app loads and renders without JavaScript errors."""
    errors: list[str] = []
    app_page.on("pageerror", lambda err: errors.append(str(err)))

    # Give time for any async errors
    app_page.wait_for_timeout(2000)

    # Take screenshot for visual verification
    app_page.screenshot(path=SCREENSHOT_DIR / "app_loaded.png")

    assert len(errors) == 0, f"JavaScript errors found: {errors}"


def test_app_has_content(app_page: Page) -> None:
    """Test that the app renders meaningful content."""
    # Flet renders to a canvas, so we check the canvas exists
    canvas = app_page.locator("canvas")
    assert canvas.count() > 0, "No canvas element found - Flet may not have initialized"

    app_page.screenshot(path=SCREENSHOT_DIR / "app_content.png")
