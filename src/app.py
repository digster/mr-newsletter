"""Main Flet application class."""

import asyncio
import logging
from typing import Optional

import flet as ft

from src.config.settings import Settings, get_settings
from src.models.base import close_db, get_async_session_maker, init_db
from src.services.auth_service import AuthService
from src.services.fetch_queue_service import FetchPriority, FetchQueueService
from src.services.gmail_service import GmailService
from src.services.newsletter_service import NewsletterService
from src.services.scheduler_service import SchedulerService
from src.ui.themes import AppTheme, BorderRadius, Colors, Spacing, Typography

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

        # Initialize services
        await self._init_services()

        # Setup routing
        self.page.on_route_change = self._on_route_change
        self.page.on_view_pop = self._on_view_pop

        # Check auth and navigate
        await self._check_auth_and_navigate()

        # Register shutdown handler for clean exit (desktop mode only)
        # Note: page.on_close is for web session expiration, NOT desktop window close.
        # In desktop mode, we use page.window.on_event to detect window close events.
        if not self.settings.flet_web_app:
            self.page.window.prevent_close = True
            self.page.window.on_event = self._on_window_event

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

    async def _on_window_event(self, e: ft.WindowEvent) -> None:
        """Handle window events for desktop mode.

        Args:
            e: Window event containing event type.
        """
        if e.type == ft.WindowEventType.CLOSE:
            logger.info("Window close event received, performing cleanup...")
            await self.shutdown()
            await self.page.window.destroy()

    def navigate(self, route: str) -> None:
        """Navigate to a route.

        Args:
            route: Route to navigate to.
        """
        self.page.go(route)

    def show_snackbar(self, message: str, error: bool = False) -> None:
        """Show a snackbar message.

        Args:
            message: Message to show.
            error: Whether this is an error message.
        """
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(
                message,
                size=Typography.BODY_SMALL_SIZE,
                color="#FFFFFF" if error else Colors.Light.TEXT_PRIMARY,
            ),
            bgcolor=Colors.Light.ERROR if error else Colors.Light.BG_TERTIARY,
        )
        self.page.snack_bar.open = True
        self.page.update()
