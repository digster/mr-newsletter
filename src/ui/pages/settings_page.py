"""Settings page for app configuration."""

from typing import TYPE_CHECKING

import flet as ft

from src.services.auth_service import AuthService

if TYPE_CHECKING:
    from src.app import NewsletterApp


class SettingsPage(ft.View):
    """Settings page for app configuration."""

    def __init__(self, app: "NewsletterApp"):
        super().__init__(route="/settings")
        self.app = app

        self.user_email_text = ft.Text("Loading...", size=14)
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
        )

        self.appbar = ft.AppBar(
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=lambda _: self.app.navigate("/home"),
            ),
            title=ft.Text("Settings"),
        )

        self.controls = [self._build_content()]

        # Load user info
        self.app.page.run_task(self._load_user_info)

    def _build_content(self) -> ft.Control:
        """Build page content."""
        return ft.Container(
            content=ft.Column(
                [
                    # Account section
                    ft.Text(
                        "Account",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(height=16),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.ACCOUNT_CIRCLE, size=48),
                                            ft.Container(width=16),
                                            ft.Column(
                                                [
                                                    ft.Text(
                                                        "Google Account",
                                                        weight=ft.FontWeight.BOLD,
                                                    ),
                                                    self.user_email_text,
                                                ],
                                                spacing=4,
                                            ),
                                        ],
                                    ),
                                    ft.Container(height=16),
                                    ft.Row(
                                        [
                                            ft.OutlinedButton(
                                                "Sign Out",
                                                icon=ft.Icons.LOGOUT,
                                                on_click=lambda e: self.app.page.run_task(
                                                    self._on_sign_out, e
                                                ),
                                            ),
                                        ],
                                    ),
                                ],
                            ),
                            padding=20,
                        ),
                    ),
                    ft.Container(height=32),
                    # Appearance section
                    ft.Text(
                        "Appearance",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(height=16),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    self.theme_dropdown,
                                ],
                            ),
                            padding=20,
                        ),
                    ),
                    ft.Container(height=32),
                    # About section
                    ft.Text(
                        "About",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(height=16),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Icon(ft.Icons.INFO_OUTLINE),
                                            ft.Container(width=12),
                                            ft.Text("Newsletter Manager"),
                                        ],
                                    ),
                                    ft.Text(
                                        "Version 0.1.0",
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                    ),
                                    ft.Container(height=8),
                                    ft.Text(
                                        "A simple newsletter reader with Gmail integration.",
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                    ),
                                ],
                            ),
                            padding=20,
                        ),
                    ),
                    ft.Container(height=32),
                    # Danger zone
                    ft.Text(
                        "Danger Zone",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.ERROR,
                    ),
                    ft.Container(height=16),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Reset OAuth Credentials",
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Text(
                                        "This will remove the stored Google OAuth client credentials. "
                                        "You'll need to reconfigure them.",
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                        size=12,
                                    ),
                                    ft.Container(height=8),
                                    ft.OutlinedButton(
                                        "Reset Credentials",
                                        icon=ft.Icons.WARNING,
                                        style=ft.ButtonStyle(
                                            color=ft.Colors.ERROR,
                                        ),
                                        on_click=lambda e: self.app.page.run_task(
                                            self._on_reset_credentials, e
                                        ),
                                    ),
                                ],
                            ),
                            padding=20,
                        ),
                    ),
                ],
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=24,
            expand=True,
        )

    async def _load_user_info(self) -> None:
        """Load user information."""
        try:
            async with self.app.get_session() as session:
                auth_service = AuthService(session)
                email = await auth_service.get_current_user_email()
                self.user_email_text.value = email or "Not signed in"
                self.app.page.update()
        except Exception as ex:
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
                self.app.page.pop_dialog(dialog)
                self.app.show_snackbar("Signed out successfully")
                self.app.navigate("/login")
            except Exception as ex:
                self.app.show_snackbar(f"Error: {ex}", error=True)

        def close_dialog(_):
            self.app.page.pop_dialog(dialog)

        dialog = ft.AlertDialog(
            title=ft.Text("Sign Out"),
            content=ft.Text("Are you sure you want to sign out?"),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.Button(
                    "Sign Out",
                    on_click=lambda e: self.app.page.run_task(confirm_sign_out, e),
                ),
            ],
        )

        self.app.page.show_dialog(dialog)

    async def _on_reset_credentials(self, e: ft.ControlEvent) -> None:
        """Handle reset credentials."""

        async def confirm_reset(e: ft.ControlEvent) -> None:
            try:
                # This would need to be implemented to clear AppCredentials
                # For now, just sign out and go to setup
                async with self.app.get_session() as session:
                    auth_service = AuthService(session)
                    await auth_service.logout()

                self.app.gmail_service = None
                self.app.page.pop_dialog(dialog)
                self.app.show_snackbar("Please reconfigure OAuth credentials")
                self.app.navigate("/setup")
            except Exception as ex:
                self.app.show_snackbar(f"Error: {ex}", error=True)

        def close_dialog(_):
            self.app.page.pop_dialog(dialog)

        dialog = ft.AlertDialog(
            title=ft.Text("Reset Credentials"),
            content=ft.Text(
                "This will remove your OAuth credentials. "
                "You'll need to reconfigure them from Google Cloud Console.\n\n"
                "Are you sure?"
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.Button(
                    "Reset",
                    color=ft.Colors.ERROR,
                    on_click=lambda e: self.app.page.run_task(confirm_reset, e),
                ),
            ],
        )

        self.app.page.show_dialog(dialog)
