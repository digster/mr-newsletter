"""Setup page for first-time OAuth configuration."""

from typing import TYPE_CHECKING

import flet as ft

from src.services.auth_service import AuthService

if TYPE_CHECKING:
    from src.app import NewsletterApp


class SetupPage(ft.View):
    """First-time setup page for OAuth credentials."""

    def __init__(self, app: "NewsletterApp"):
        super().__init__(route="/setup")
        self.app = app

        # Form fields
        self.client_id_field = ft.TextField(
            label="Client ID",
            hint_text="Enter your Google OAuth Client ID",
            width=500,
        )
        self.client_secret_field = ft.TextField(
            label="Client Secret",
            hint_text="Enter your Google OAuth Client Secret",
            password=True,
            can_reveal_password=True,
            width=500,
        )
        self.error_text = ft.Text(
            "",
            color=ft.Colors.ERROR,
            visible=False,
        )
        self.loading = ft.ProgressRing(visible=False)

        self.controls = [self._build_content()]

    def _build_content(self) -> ft.Control:
        """Build page content."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(height=50),
                    ft.Text(
                        "Newsletter Manager",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(height=20),
                    ft.Text(
                        "Welcome! Let's set up your Google OAuth credentials.",
                        size=16,
                    ),
                    ft.Container(height=30),
                    ft.Card(
                        content=ft.Container(
                            content=ft.Column(
                                [
                                    ft.Text(
                                        "Google Cloud Console Setup",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                    ),
                                    ft.Container(height=10),
                                    ft.Text(
                                        "1. Go to Google Cloud Console",
                                        size=14,
                                    ),
                                    ft.Text(
                                        "2. Create a new project or select existing",
                                        size=14,
                                    ),
                                    ft.Text(
                                        "3. Enable the Gmail API",
                                        size=14,
                                    ),
                                    ft.Text(
                                        "4. Configure OAuth consent screen",
                                        size=14,
                                    ),
                                    ft.Text(
                                        "5. Create OAuth 2.0 Client ID (Desktop app)",
                                        size=14,
                                    ),
                                    ft.Text(
                                        "6. Copy the Client ID and Client Secret below",
                                        size=14,
                                    ),
                                    ft.Container(height=10),
                                    ft.TextButton(
                                        "Open Google Cloud Console",
                                        icon=ft.Icons.OPEN_IN_NEW,
                                        url="https://console.cloud.google.com/apis/credentials",
                                    ),
                                ],
                            ),
                            padding=20,
                        ),
                        width=500,
                    ),
                    ft.Container(height=30),
                    self.client_id_field,
                    ft.Container(height=10),
                    self.client_secret_field,
                    ft.Container(height=10),
                    self.error_text,
                    ft.Container(height=20),
                    ft.Row(
                        [
                            self.loading,
                            ft.Button(
                                "Save & Continue",
                                icon=ft.Icons.ARROW_FORWARD,
                                on_click=lambda e: self.app.page.run_task(
                                    self._on_save, e
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=40,
            expand=True,
        )

    async def _on_save(self, e: ft.ControlEvent) -> None:
        """Handle save button click."""
        client_id = self.client_id_field.value.strip()
        client_secret = self.client_secret_field.value.strip()

        # Validate
        if not client_id:
            self._show_error("Client ID is required")
            return
        if not client_secret:
            self._show_error("Client Secret is required")
            return

        self.loading.visible = True
        self.error_text.visible = False
        self.app.page.update()

        try:
            async with self.app.get_session() as session:
                auth_service = AuthService(session)
                success = await auth_service.save_app_credentials(
                    client_id=client_id,
                    client_secret=client_secret,
                )

                if success:
                    self.app.show_snackbar("Credentials saved successfully!")
                    self.app.navigate("/login")
                else:
                    self._show_error("Failed to save credentials")
        except Exception as ex:
            self._show_error(f"Error: {str(ex)}")
        finally:
            self.loading.visible = False
            self.app.page.update()

    def _show_error(self, message: str) -> None:
        """Show error message."""
        self.error_text.value = message
        self.error_text.visible = True
        self.app.page.update()
