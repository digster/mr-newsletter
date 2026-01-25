"""Login page for Gmail OAuth with sophisticated styling."""

from typing import TYPE_CHECKING

import flet as ft

from src.services.auth_service import AuthService
from src.services.gmail_service import GmailService
from src.ui.themes import BorderRadius, Colors, Spacing, Typography, get_colors

if TYPE_CHECKING:
    from src.app import NewsletterApp


class LoginPage(ft.View):
    """Login page with Gmail OAuth and clean design."""

    def __init__(self, app: "NewsletterApp"):
        super().__init__(route="/login")
        self.app = app

        # Get theme-aware colors
        self.colors = get_colors(self.app.page)

        self.error_text = ft.Text(
            "",
            size=Typography.BODY_SMALL_SIZE,
            color=self.colors.ERROR,
            visible=False,
        )
        self.loading = ft.ProgressRing(
            visible=False,
            width=20,
            height=20,
            stroke_width=2,
            color=self.colors.ACCENT,
        )
        self.status_text = ft.Text(
            "",
            size=Typography.BODY_SMALL_SIZE,
            color=self.colors.TEXT_SECONDARY,
            visible=False,
        )

        self.controls = [self._build_content()]

    def _build_content(self) -> ft.Control:
        """Build page content."""
        c = self.colors  # Shorthand for readability
        return ft.Container(
            content=ft.Column(
                [
                    ft.Container(expand=True),
                    # Brand/Logo
                    ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.MARK_EMAIL_READ,
                                size=32,
                                color=c.ACCENT,
                            ),
                            ft.Container(width=Spacing.SM),
                            ft.Text(
                                "Newsletter",
                                size=Typography.H2_SIZE,
                                weight=ft.FontWeight.W_600,
                                color=c.TEXT_PRIMARY,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Container(height=Spacing.XL),
                    # Description
                    ft.Text(
                        "Sign in to access your newsletters",
                        size=Typography.BODY_SIZE,
                        color=c.TEXT_SECONDARY,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=Spacing.XL),
                    # Error/status area
                    ft.Container(
                        content=ft.Column(
                            [
                                self.error_text,
                                self.status_text,
                            ],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=Spacing.XS,
                        ),
                        height=40,
                    ),
                    ft.Container(height=Spacing.MD),
                    # Sign in button
                    ft.Container(
                        content=ft.ElevatedButton(
                            content=ft.Row(
                                [
                                    self.loading,
                                    ft.Container(width=Spacing.XS)
                                    if not self.loading.visible
                                    else ft.Container(),
                                    ft.Icon(
                                        ft.Icons.LOGIN,
                                        size=18,
                                        color="#FFFFFF",
                                    ),
                                    ft.Container(width=Spacing.XS),
                                    ft.Text(
                                        "Sign in with Google",
                                        size=Typography.BODY_SIZE,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=0,
                            ),
                            bgcolor=c.ACCENT,
                            color="#FFFFFF",
                            height=48,
                            width=240,
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
                                elevation=0,
                            ),
                            on_click=lambda e: self.app.page.run_task(
                                self._on_sign_in, e
                            ),
                        ),
                    ),
                    ft.Container(expand=True),
                    # Footer
                    ft.Text(
                        "Your data stays private and secure",
                        size=Typography.CAPTION_SIZE,
                        color=c.TEXT_TERTIARY,
                    ),
                    ft.Container(height=Spacing.XL),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            bgcolor=c.BG_PRIMARY,
            padding=Spacing.XL,
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
                    real_email = await self.app.gmail_service.get_user_email_async()
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
