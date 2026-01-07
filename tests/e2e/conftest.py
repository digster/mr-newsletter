"""E2E test fixtures for Playwright browser testing."""

import os
import subprocess
import time
from collections.abc import Generator

import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def flet_app() -> Generator[subprocess.Popen[bytes], None, None]:
    """Start the Flet web app for testing."""
    env = os.environ.copy()
    env["FLET_WEB_APP"] = "true"
    env["ENVIRONMENT"] = "test"

    proc = subprocess.Popen(
        ["uv", "run", "python", "-m", "src.main"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    time.sleep(5)  # Wait for Flet app to initialize
    yield proc
    proc.terminate()
    proc.wait()


@pytest.fixture
def app_page(page: Page, flet_app: subprocess.Popen[bytes]) -> Page:
    """Navigate to the Flet app and return the page."""
    page.goto("http://127.0.0.1:8550")
    page.wait_for_load_state("networkidle")
    return page
