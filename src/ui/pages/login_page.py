"""Login page for Gmail OAuth."""

from typing import TYPE_CHECKING

import flet as ft

from src.services.auth_service import AuthService
from src.services.gmail_service import GmailService

if TYPE_CHECKING:
    from src.app import NewsletterApp


class LoginPage(ft.View):
    """Login page with Gmail OAuth."""

    def __init__(self, app: "NewsletterApp"):
        super().__init__(route="/login")
        self.app = app

        self.error_text = ft.Text(
            "",
            color=ft.colors.ERROR,
            visible=False,
        )
        self.loading = ft.ProgressRing(visible=False)
        self.status_text = ft.Text(
            "",
            visible=False,
        )

        self.controls = [self._build_content()]

    def _build_content(self) -> ft.Control:
        """Build page content."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(height=100),
                    ft.Icon(
                        ft.icons.EMAIL_OUTLINED,
                        size=80,
                        color=ft.colors.PRIMARY,
                    ),
                    ft.Container(height=20),
                    ft.Text(
                        "Newsletter Manager",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Container(height=10),
                    ft.Text(
                        "Sign in with your Google account to access your newsletters",
                        size=16,
                        color=ft.colors.ON_SURFACE_VARIANT,
                    ),
                    ft.Container(height=40),
                    self.error_text,
                    self.status_text,
                    ft.Container(height=20),
                    ft.Row(
                        [
                            self.loading,
                            ft.ElevatedButton(
                                "Sign in with Google",
                                icon=ft.icons.LOGIN,
                                on_click=self._on_sign_in,
                                style=ft.ButtonStyle(
                                    padding=20,
                                ),
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Container(height=40),
                    ft.TextButton(
                        "Change OAuth Credentials",
                        on_click=lambda _: self.app.navigate("/setup"),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=40,
            expand=True,
        )

    async def _on_sign_in(self, e: ft.ControlEvent) -> None:
        """Handle sign in button click."""
        self.loading.visible = True
        self.error_text.visible = False
        self.status_text.value = "Opening browser for authentication..."
        self.status_text.visible = True
        self.app.page.update()

        try:
            async with self.app.get_session() as session:
                auth_service = AuthService(session)

                # Start OAuth flow
                self.status_text.value = "Waiting for authentication..."
                self.app.page.update()

                auth_result = await auth_service.start_oauth_flow()

                if auth_result.success:
                    # Initialize Gmail service
                    self.app.gmail_service = GmailService(auth_result.credentials)

                    # Get real email and update
                    real_email = self.app.gmail_service.get_user_email()
                    if real_email and auth_result.user_email != real_email:
                        await auth_service.update_user_email(
                            auth_result.user_email or "user@gmail.com",
                            real_email,
                        )

                    self.app.show_snackbar(f"Signed in as {real_email}")
                    self.app.navigate("/home")
                else:
                    self._show_error(auth_result.error or "Authentication failed")
        except Exception as ex:
            self._show_error(f"Error: {str(ex)}")
        finally:
            self.loading.visible = False
            self.status_text.visible = False
            self.app.page.update()

    def _show_error(self, message: str) -> None:
        """Show error message."""
        self.error_text.value = message
        self.error_text.visible = True
        self.app.page.update()
