"""Settings page for app configuration with sophisticated styling."""

from typing import TYPE_CHECKING

import flet as ft

from src.services.auth_service import AuthService
from src.services.newsletter_service import NewsletterService
from src.ui.components import ConfirmDialog, Sidebar
from src.ui.themes import BorderRadius, Colors, Spacing, Typography

if TYPE_CHECKING:
    from src.app import NewsletterApp


class SettingsPage(ft.View):
    """Settings page for app configuration with sidebar."""

    def __init__(self, app: "NewsletterApp"):
        super().__init__(route="/settings", padding=0, spacing=0)
        self.app = app
        self.newsletters = []

        self.user_email_text = ft.Text(
            "Loading...",
            size=Typography.BODY_SIZE,
            color=Colors.Light.TEXT_SECONDARY,
        )

        self.theme_dropdown = ft.Dropdown(
            label="Theme",
            value="system",
            options=[
                ft.dropdown.Option("system", "System"),
                ft.dropdown.Option("light", "Light"),
                ft.dropdown.Option("dark", "Dark"),
            ],
            on_select=self._on_theme_change,
            width=200,
            border_radius=BorderRadius.SM,
            content_padding=ft.padding.symmetric(
                horizontal=Spacing.SM, vertical=Spacing.SM
            ),
            text_size=Typography.BODY_SIZE,
        )

        self.sidebar = Sidebar(
            current_route="/settings",
            newsletters=[],
            on_navigate=self._handle_navigate,
        )

        self.controls = [self._build_content()]

        # Load data
        self.app.page.run_task(self._load_data)

    def _build_content(self) -> ft.Control:
        """Build page content with sidebar."""
        return ft.Row(
            [
                # Sidebar
                self.sidebar,
                # Main content
                ft.Container(
                    content=ft.Column(
                        [
                            # Page header
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.IconButton(
                                            icon=ft.Icons.ARROW_BACK,
                                            icon_color=Colors.Light.TEXT_SECONDARY,
                                            icon_size=20,
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(
                                                    radius=BorderRadius.SM
                                                ),
                                            ),
                                            on_click=lambda _: self.app.navigate(
                                                "/home"
                                            ),
                                        ),
                                        ft.Container(width=Spacing.XS),
                                        ft.Text(
                                            "Settings",
                                            size=Typography.H1_SIZE,
                                            weight=ft.FontWeight.W_600,
                                            color=Colors.Light.TEXT_PRIMARY,
                                        ),
                                    ],
                                ),
                                padding=ft.padding.only(bottom=Spacing.XL),
                            ),
                            # Settings content
                            ft.Container(
                                content=ft.Column(
                                    [
                                        # Account section
                                        self._build_section(
                                            "Account",
                                            ft.Column(
                                                [
                                                    ft.Row(
                                                        [
                                                            ft.CircleAvatar(
                                                                content=ft.Icon(
                                                                    ft.Icons.PERSON,
                                                                    size=20,
                                                                    color=Colors.Light.TEXT_PRIMARY,
                                                                ),
                                                                radius=24,
                                                                bgcolor=Colors.Light.BG_TERTIARY,
                                                            ),
                                                            ft.Container(width=Spacing.MD),
                                                            ft.Column(
                                                                [
                                                                    ft.Text(
                                                                        "Google Account",
                                                                        size=Typography.BODY_SIZE,
                                                                        weight=ft.FontWeight.W_500,
                                                                        color=Colors.Light.TEXT_PRIMARY,
                                                                    ),
                                                                    self.user_email_text,
                                                                ],
                                                                spacing=Spacing.XXS,
                                                            ),
                                                        ],
                                                    ),
                                                    ft.Container(height=Spacing.MD),
                                                    ft.OutlinedButton(
                                                        content=ft.Row(
                                                            [
                                                                ft.Icon(
                                                                    ft.Icons.LOGOUT,
                                                                    size=16,
                                                                    color=Colors.Light.ERROR,
                                                                ),
                                                                ft.Container(
                                                                    width=Spacing.XS
                                                                ),
                                                                ft.Text(
                                                                    "Sign Out",
                                                                    color=Colors.Light.ERROR,
                                                                ),
                                                            ],
                                                        ),
                                                        style=ft.ButtonStyle(
                                                            side=ft.BorderSide(
                                                                1, Colors.Light.ERROR
                                                            ),
                                                            shape=ft.RoundedRectangleBorder(
                                                                radius=BorderRadius.SM
                                                            ),
                                                        ),
                                                        on_click=lambda e: self.app.page.run_task(
                                                            self._on_sign_out, e
                                                        ),
                                                    ),
                                                ],
                                            ),
                                        ),
                                        ft.Container(height=Spacing.LG),
                                        # Appearance section
                                        self._build_section(
                                            "Appearance",
                                            self.theme_dropdown,
                                        ),
                                        ft.Container(height=Spacing.LG),
                                        # About section
                                        self._build_section(
                                            "About",
                                            ft.Column(
                                                [
                                                    ft.Row(
                                                        [
                                                            ft.Icon(
                                                                ft.Icons.MARK_EMAIL_READ,
                                                                size=20,
                                                                color=Colors.Light.ACCENT,
                                                            ),
                                                            ft.Container(width=Spacing.XS),
                                                            ft.Text(
                                                                "Newsletter Reader",
                                                                size=Typography.BODY_SIZE,
                                                                weight=ft.FontWeight.W_500,
                                                                color=Colors.Light.TEXT_PRIMARY,
                                                            ),
                                                        ],
                                                    ),
                                                    ft.Container(height=Spacing.XS),
                                                    ft.Text(
                                                        "Version 0.1.0",
                                                        size=Typography.CAPTION_SIZE,
                                                        color=Colors.Light.TEXT_TERTIARY,
                                                        font_family="monospace",
                                                    ),
                                                    ft.Container(height=Spacing.SM),
                                                    ft.Text(
                                                        "A simple newsletter reader with Gmail integration.",
                                                        size=Typography.BODY_SMALL_SIZE,
                                                        color=Colors.Light.TEXT_SECONDARY,
                                                    ),
                                                ],
                                                spacing=0,
                                            ),
                                        ),
                                    ],
                                    scroll=ft.ScrollMode.AUTO,
                                ),
                                expand=True,
                            ),
                        ],
                        expand=True,
                    ),
                    padding=Spacing.LG,
                    expand=True,
                    bgcolor=Colors.Light.BG_SECONDARY,
                ),
            ],
            expand=True,
            spacing=0,
        )

    def _build_section(self, title: str, content: ft.Control) -> ft.Control:
        """Build a settings section with title and card."""
        return ft.Column(
            [
                ft.Text(
                    title.upper(),
                    size=11,
                    weight=ft.FontWeight.W_500,
                    color=Colors.Light.TEXT_TERTIARY,
                ),
                ft.Container(height=Spacing.SM),
                ft.Container(
                    content=content,
                    padding=Spacing.MD,
                    border_radius=BorderRadius.MD,
                    border=ft.border.all(1, Colors.Light.BORDER_DEFAULT),
                    bgcolor=Colors.Light.BG_PRIMARY,
                ),
            ],
            spacing=0,
        )

    def _handle_navigate(self, route: str) -> None:
        """Handle navigation from sidebar."""
        self.app.navigate(route)

    async def _load_data(self) -> None:
        """Load user information and newsletters."""
        try:
            async with self.app.get_session() as session:
                # Load user info
                auth_service = AuthService(session)
                email = await auth_service.get_current_user_email()
                self.user_email_text.value = email or "Not signed in"

                # Load newsletters for sidebar
                newsletter_service = NewsletterService(session=session)
                self.newsletters = await newsletter_service.get_all_newsletters()

            # Update sidebar
            self.sidebar.update_newsletters(self.newsletters)
            self.app.page.update()
        except Exception:
            self.user_email_text.value = "Error loading user info"
            self.app.page.update()

    def _on_theme_change(self, e: ft.ControlEvent) -> None:
        """Handle theme change."""
        theme_value = self.theme_dropdown.value
        if theme_value == "light":
            self.app.page.theme_mode = ft.ThemeMode.LIGHT
        elif theme_value == "dark":
            self.app.page.theme_mode = ft.ThemeMode.DARK
        else:
            self.app.page.theme_mode = ft.ThemeMode.SYSTEM
        self.app.page.update()

    async def _on_sign_out(self, e: ft.ControlEvent) -> None:
        """Handle sign out."""

        async def confirm_sign_out(e: ft.ControlEvent) -> None:
            try:
                async with self.app.get_session() as session:
                    auth_service = AuthService(session)
                    await auth_service.logout()

                self.app.gmail_service = None
                dialog.open = False
                self.app.page.update()
                self.app.show_snackbar("Signed out successfully")
                self.app.navigate("/login")
            except Exception as ex:
                self.app.show_snackbar(f"Error: {ex}", error=True)

        def close_dialog(_):
            dialog.open = False
            self.app.page.update()

        dialog = ConfirmDialog(
            title="Sign Out",
            message="Are you sure you want to sign out?",
            confirm_text="Sign Out",
            cancel_text="Cancel",
            is_destructive=True,
            on_confirm=lambda e: self.app.page.run_task(confirm_sign_out, e),
            on_cancel=close_dialog,
        )

        self.app.page.show_dialog(dialog)
