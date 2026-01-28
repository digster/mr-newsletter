"""Main Flet application class."""

import asyncio
import logging
from typing import Optional

import flet as ft

from src.config.settings import Settings, get_settings
from src.models.base import close_db, get_async_session_maker, init_db
from src.repositories.user_settings_repository import UserSettingsRepository
from src.services.auth_service import AuthService
from src.services.fetch_queue_service import FetchPriority, FetchQueueService
from src.services.gmail_service import GmailService
from src.services.newsletter_service import NewsletterService
from src.services.scheduler_service import SchedulerService
from src.services.theme_service import ThemeService
from src.ui.themes import AppTheme, BorderRadius, Colors, Spacing, Typography, set_active_theme_colors

logger = logging.getLogger(__name__)


class NewsletterApp:
    """Main application orchestrator."""

    def __init__(self, page: ft.Page):
        """Initialize the application.

        Args:
            page: Flet page instance.
        """
        self.page = page
        self.settings: Settings = get_settings()

        # Services (initialized lazily)
        self.auth_service: Optional[AuthService] = None
        self.gmail_service: Optional[GmailService] = None
        self.newsletter_service: Optional[NewsletterService] = None
        self.scheduler_service: Optional[SchedulerService] = None
        self.fetch_queue_service: Optional[FetchQueueService] = None

        # Session maker
        self._session_maker = None

    async def initialize(self) -> None:
        """Initialize the application."""
        # Configure page
        self.page.title = "Newsletter Reader"
        self.page.theme_mode = ft.ThemeMode.SYSTEM
        self.page.padding = 0
        self.page.spacing = 0

        # Apply new theme
        self.page.theme = AppTheme.get_light_theme()
        self.page.dark_theme = AppTheme.get_dark_theme()

        # Window settings
        self.page.window.width = 1200
        self.page.window.height = 800
        self.page.window.min_width = 900
        self.page.window.min_height = 600

        # Initialize database
        await init_db()
        self._session_maker = get_async_session_maker()

        # Load and apply saved theme
        await self._load_and_apply_theme()

        # Initialize services
        await self._init_services()

        # Setup routing
        self.page.on_route_change = self._on_route_change
        self.page.on_view_pop = self._on_view_pop

        # Check auth and navigate
        await self._check_auth_and_navigate()

        # Register shutdown handler for clean exit
        self.page.on_close = lambda e: asyncio.create_task(self.shutdown())

    async def _load_and_apply_theme(self) -> None:
        """Load and apply the user's saved theme on startup."""
        try:
            async with self._session_maker() as session:
                settings_repo = UserSettingsRepository(session)
                user_settings = await settings_repo.get_settings()

            # Get active theme filename
            active_theme = user_settings.active_theme or "default.json"

            # Load and apply theme
            theme_service = ThemeService()
            success, theme, error = theme_service.load_theme(active_theme)

            if success and theme:
                # Apply theme colors to the cache
                light_colors, dark_colors = theme_service.apply_theme(theme)

                # Update Flet page themes
                self.page.theme = AppTheme.create_theme_from_colors(light_colors)
                self.page.dark_theme = AppTheme.create_theme_from_colors(dark_colors, is_dark=True)

                logger.info(f"Applied saved theme: {theme.metadata.name}")
            else:
                # Fall back to defaults if theme loading fails
                logger.warning(f"Failed to load theme '{active_theme}': {error}")
                self.page.theme = AppTheme.get_light_theme()
                self.page.dark_theme = AppTheme.get_dark_theme()

        except Exception as e:
            logger.warning(f"Error loading theme: {e}, using defaults")
            self.page.theme = AppTheme.get_light_theme()
            self.page.dark_theme = AppTheme.get_dark_theme()

    async def _init_services(self) -> None:
        """Initialize application services."""
        # Scheduler
        if self.settings.scheduler_enabled:
            self.scheduler_service = SchedulerService()
            self.scheduler_service.initialize(
                fetch_callback=self._scheduled_fetch_callback
            )

        # Fetch queue
        self.fetch_queue_service = FetchQueueService(
            delay_seconds=self.settings.fetch_queue_delay_seconds,
            fetch_callback=self._queue_fetch_callback,
        )

    async def _scheduled_fetch_callback(self, newsletter_id: int) -> None:
        """Callback for scheduled newsletter fetch.

        Args:
            newsletter_id: Newsletter to fetch.
        """
        if self.fetch_queue_service:
            await self.fetch_queue_service.queue_fetch(
                newsletter_id, FetchPriority.NORMAL
            )

    async def _queue_fetch_callback(self, newsletter_id: int) -> int:
        """Callback for queue-based newsletter fetch.

        Args:
            newsletter_id: Newsletter to fetch.

        Returns:
            Number of emails fetched.
        """
        async with self._session_maker() as session:
            newsletter_service = NewsletterService(
                session=session,
                gmail_service=self.gmail_service,
            )
            return await newsletter_service.fetch_newsletter_emails(newsletter_id)

    async def _check_auth_and_navigate(self) -> None:
        """Check authentication status and navigate appropriately."""
        async with self._session_maker() as session:
            auth_service = AuthService(session)

            # Check if app is configured via environment variables
            if not await auth_service.is_app_configured():
                self.page.go("/config-error")
                return

            # Check if user is authenticated
            auth_result = await auth_service.get_user_credentials()
            if auth_result.success:
                # Initialize Gmail service
                self.gmail_service = GmailService(auth_result.credentials)
                self.page.go("/home")
            else:
                self.page.go("/login")

    async def _on_route_change(self, route: ft.RouteChangeEvent) -> None:
        """Handle route changes.

        Args:
            route: Route change event.
        """
        self.page.views.clear()

        # Import pages here to avoid circular imports
        from src.ui.pages.email_list_page import EmailListPage
        from src.ui.pages.email_reader_page import EmailReaderPage
        from src.ui.pages.home_page import HomePage
        from src.ui.pages.login_page import LoginPage
        from src.ui.pages.newsletters_page import NewslettersPage
        from src.ui.pages.settings_page import SettingsPage

        # Route to appropriate page
        if self.page.route == "/config-error":
            self.page.views.append(self._create_config_error_view())
        elif self.page.route == "/login":
            self.page.views.append(LoginPage(self))
        elif self.page.route == "/home":
            self.page.views.append(HomePage(self))
        elif self.page.route == "/newsletters":
            self.page.views.append(NewslettersPage(self))
        elif self.page.route.startswith("/newsletter/"):
            newsletter_id = int(self.page.route.split("/")[-1])
            self.page.views.append(EmailListPage(self, newsletter_id))
        elif self.page.route.startswith("/email/"):
            email_id = int(self.page.route.split("/")[-1])
            self.page.views.append(EmailReaderPage(self, email_id))
        elif self.page.route == "/settings":
            self.page.views.append(SettingsPage(self))
        else:
            # Default to home or config error
            async with self._session_maker() as session:
                auth_service = AuthService(session)
                if await auth_service.is_app_configured():
                    self.page.views.append(HomePage(self))
                else:
                    self.page.views.append(self._create_config_error_view())

        self.page.update()

    def _on_view_pop(self, view: ft.ViewPopEvent) -> None:
        """Handle view pop (back navigation).

        Args:
            view: View pop event.
        """
        self.page.views.pop()
        top_view = self.page.views[-1] if self.page.views else None
        if top_view:
            self.page.go(top_view.route)

    def _create_config_error_view(self) -> ft.View:
        """Create an error view for missing OAuth configuration.

        Returns:
            View showing configuration error message.
        """
        return ft.View(
            route="/config-error",
            padding=0,
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(
                                ft.Icons.ERROR_OUTLINE,
                                size=48,
                                color=Colors.Light.ERROR,
                            ),
                            ft.Container(height=Spacing.LG),
                            ft.Text(
                                "Configuration Required",
                                size=Typography.H2_SIZE,
                                weight=ft.FontWeight.W_600,
                                color=Colors.Light.TEXT_PRIMARY,
                            ),
                            ft.Container(height=Spacing.MD),
                            ft.Text(
                                "Google OAuth credentials are not configured.",
                                size=Typography.BODY_SIZE,
                                color=Colors.Light.TEXT_SECONDARY,
                            ),
                            ft.Container(height=Spacing.XS),
                            ft.Text(
                                "Please set the following environment variables:",
                                size=Typography.BODY_SMALL_SIZE,
                                color=Colors.Light.TEXT_TERTIARY,
                            ),
                            ft.Container(height=Spacing.MD),
                            ft.Container(
                                content=ft.Column(
                                    controls=[
                                        ft.Text(
                                            "GOOGLE_CLIENT_ID",
                                            font_family="monospace",
                                            size=Typography.BODY_SIZE,
                                            weight=ft.FontWeight.W_500,
                                            color=Colors.Light.TEXT_PRIMARY,
                                        ),
                                        ft.Text(
                                            "GOOGLE_CLIENT_SECRET",
                                            font_family="monospace",
                                            size=Typography.BODY_SIZE,
                                            weight=ft.FontWeight.W_500,
                                            color=Colors.Light.TEXT_PRIMARY,
                                        ),
                                    ],
                                    spacing=Spacing.XXS,
                                ),
                                padding=Spacing.MD,
                                bgcolor=Colors.Light.BG_TERTIARY,
                                border_radius=BorderRadius.MD,
                            ),
                            ft.Container(height=Spacing.MD),
                            ft.Text(
                                "Get these from Google Cloud Console:",
                                size=Typography.BODY_SMALL_SIZE,
                                color=Colors.Light.TEXT_TERTIARY,
                            ),
                            ft.Container(height=Spacing.XS),
                            ft.TextButton(
                                content=ft.Text(
                                    "console.cloud.google.com/apis/credentials",
                                    size=Typography.BODY_SMALL_SIZE,
                                    color=Colors.Light.ACCENT,
                                ),
                                url="https://console.cloud.google.com/apis/credentials",
                            ),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    expand=True,
                    alignment=ft.alignment.Alignment.CENTER,
                    padding=Spacing.XL,
                    bgcolor=Colors.Light.BG_PRIMARY,
                )
            ],
        )

    def get_session(self):
        """Get an async session for database operations.

        Returns:
            Async session context manager.
        """
        return self._session_maker()

    async def shutdown(self) -> None:
        """Clean shutdown of application."""
        if self.scheduler_service:
            self.scheduler_service.shutdown()

        if self.fetch_queue_service:
            await self.fetch_queue_service.stop()

        await close_db()
        logger.info("Application shutdown complete")

    def navigate(self, route: str) -> None:
        """Navigate to a route.

        Args:
            route: Route to navigate to.
        """
        self.page.go(route)

    def show_snackbar(self, message: str, error: bool = False) -> None:
        """Show a notification message.

        Args:
            message: Message to show.
            error: Whether this is an error message.

        Note: Uses AlertDialog added to overlay as a workaround for SnackBar
        visibility issues in Flet 0.80 web mode with Views and async contexts.
        """

        def close_dialog(e: ft.ControlEvent) -> None:
            dialog.open = False
            if dialog in self.page.overlay:
                self.page.overlay.remove(dialog)
            self.page.update()

        dialog = ft.AlertDialog(
            modal=False,
            title=ft.Text(
                "Error" if error else "Success",
                size=16,
                weight=ft.FontWeight.W_500,
            ),
            content=ft.Text(message, size=Typography.BODY_SMALL_SIZE),
            actions=[
                ft.TextButton("OK", on_click=close_dialog),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            open=True,
        )
        # Add to overlay for proper z-index in View-based layouts
        self.page.overlay.append(dialog)
        self.page.update()
