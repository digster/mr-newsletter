"""E2E test fixtures for Playwright browser testing with VNC support."""

import os
import subprocess
import time
from collections.abc import Generator
from typing import Any

import httpx
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright


# VNC Browser Container configuration
VNC_SERVER_URL = os.environ.get("VNC_SERVER_URL", "http://localhost:3001")
USE_VNC_BROWSER = os.environ.get("USE_VNC_BROWSER", "true").lower() == "true"

# App configuration - use host.docker.internal when running in VNC container
APP_HOST = os.environ.get("APP_HOST", "host.docker.internal" if USE_VNC_BROWSER else "127.0.0.1")
APP_PORT = os.environ.get("APP_PORT", "8550")
APP_URL = f"http://{APP_HOST}:{APP_PORT}"


def get_vnc_ws_endpoint() -> str:
    """Fetch the WebSocket endpoint from the VNC Playwright server."""
    try:
        response = httpx.get(f"{VNC_SERVER_URL}/json", timeout=5.0)
        data = response.json()
        ws_path = data.get("wsEndpointPath", "")
        # Convert HTTP URL to WebSocket URL
        ws_url = VNC_SERVER_URL.replace("http://", "ws://").replace("https://", "wss://")
        return f"{ws_url}{ws_path}"
    except Exception as e:
        raise RuntimeError(f"Failed to get VNC WebSocket endpoint: {e}") from e


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest to use VNC browser by default."""
    # Set default browser to chromium to avoid parametrization
    if not config.getoption("--browser", default=None):
        config.option.browser = ["chromium"]


@pytest.fixture(scope="session")
def base_url() -> str:
    """Return the base URL for the app (required by pytest-base-url)."""
    return APP_URL


@pytest.fixture(scope="session")
def browser_type_launch_args() -> dict[str, Any]:
    """Override launch args - not used when connecting to remote browser."""
    return {}


@pytest.fixture(scope="session")
def _playwright() -> Generator[Playwright, None, None]:
    """Create a Playwright instance for the session."""
    with sync_playwright() as p:
        yield p


@pytest.fixture(scope="session")
def browser(_playwright: Playwright) -> Generator[Browser, None, None]:
    """
    Connect to the VNC browser container or launch a local browser.

    This fixture overrides pytest-playwright's browser fixture.
    Set USE_VNC_BROWSER=false to use local Chromium instead.
    """
    if USE_VNC_BROWSER:
        ws_endpoint = get_vnc_ws_endpoint()
        print(f"\n🌐 Connecting to VNC browser at: {ws_endpoint}")
        browser = _playwright.chromium.connect(ws_endpoint)
        yield browser
        browser.close()
    else:
        print("\n🖥️  Launching local Chromium browser")
        browser = _playwright.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture(scope="function")
def context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Create a new browser context for each test."""
    ctx = browser.new_context(
        viewport={"width": 1280, "height": 720},
        ignore_https_errors=True,
    )
    yield ctx
    ctx.close()


@pytest.fixture(scope="function")
def page(context: BrowserContext) -> Generator[Page, None, None]:
    """Create a new page for each test."""
    pg = context.new_page()
    yield pg
    pg.close()


@pytest.fixture(scope="session")
def flet_app() -> Generator[subprocess.Popen[bytes] | None, None, None]:
    """
    Start the Flet web app for testing.

    Note: When using VNC browser, the app should already be running
    since the container can't access the host's subprocess.
    """
    # Check if app is already running
    try:
        response = httpx.get(f"http://127.0.0.1:{APP_PORT}/", timeout=2.0)
        if response.status_code == 200:
            print(f"\n✅ App already running at http://127.0.0.1:{APP_PORT}")
            yield None
            return
    except Exception:
        pass

    # Start the app if not running
    print(f"\n🚀 Starting Flet app on port {APP_PORT}...")
    env = os.environ.copy()
    env["FLET_WEB_APP"] = "true"
    env["ENVIRONMENT"] = "test"

    proc = subprocess.Popen(
        ["uv", "run", "flet", "run", "--web", "--port", APP_PORT, "src/main.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(8)  # Wait for Flet app to initialize
    yield proc
    proc.terminate()
    proc.wait()


@pytest.fixture
def app_page(page: Page, flet_app: Any) -> Page:
    """Navigate to the Flet app and return the page."""
    page.goto(APP_URL)
    page.wait_for_load_state("networkidle")
    return page
