"""Application entry point."""

import asyncio
import atexit
import logging
import sys

import flet as ft

from src.app import NewsletterApp
from src.config.settings import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def main(page: ft.Page) -> None:
    """Main entry point for Flet application.

    Args:
        page: Flet page instance.
    """
    app = NewsletterApp(page)

    # Register atexit cleanup for abnormal exits (e.g., force quit via Dock)
    def cleanup_sync():
        try:
            # Try to run shutdown synchronously if possible
            try:
                loop = asyncio.get_running_loop()
                # If loop is running, we can't do much here
            except RuntimeError:
                # No running loop, can create one
                asyncio.run(app.shutdown())
        except Exception:
            pass  # Best effort cleanup

    atexit.register(cleanup_sync)

    await app.initialize()


def run() -> None:
    """Run the application."""
    settings = get_settings()

    logger.info(f"Starting Newsletter Manager in {settings.environment} mode")

    # Configure Flet app options
    app_kwargs = {
        "port": settings.flet_port,
    }

    if settings.flet_web_app:
        # Web app mode
        app_kwargs["view"] = ft.AppView.WEB_BROWSER
        app_kwargs["host"] = settings.flet_host
    else:
        # Desktop app mode
        app_kwargs["view"] = ft.AppView.FLET_APP

    ft.run(main, **app_kwargs)


if __name__ == "__main__":
    run()
