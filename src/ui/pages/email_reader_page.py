"""Email reader page for viewing email content."""

import base64
from typing import TYPE_CHECKING, Optional

import flet as ft
from flet_webview import WebView

from src.services.email_service import EmailService
from src.utils.html_sanitizer import sanitize_html_for_webview

if TYPE_CHECKING:
    from src.app import NewsletterApp


class EmailReaderPage(ft.View):
    """Page for reading email content."""

    def __init__(self, app: "NewsletterApp", email_id: int):
        super().__init__(route=f"/email/{email_id}")
        self.app = app
        self.email_id = email_id
        self.email = None

        self.content_area = ft.Container(expand=True)
        self.loading = ft.ProgressRing(visible=False)
        self.title_text = ft.Text("Loading...", size=16)

        self.star_button = ft.IconButton(
            icon=ft.Icons.STAR_BORDER,
            tooltip="Star",
            on_click=lambda e: self.app.page.run_task(self._toggle_star, e),
        )

        self.appbar = ft.AppBar(
            leading=ft.IconButton(
                icon=ft.Icons.ARROW_BACK,
                on_click=self._go_back,
            ),
            title=self.title_text,
            actions=[
                self.star_button,
                ft.IconButton(
                    icon=ft.Icons.MARK_EMAIL_UNREAD,
                    tooltip="Mark as unread",
                    on_click=lambda e: self.app.page.run_task(self._mark_unread, e),
                ),
                ft.IconButton(
                    icon=ft.Icons.ARCHIVE,
                    tooltip="Archive",
                    on_click=lambda e: self.app.page.run_task(self._archive, e),
                ),
            ],
        )

        self.controls = [self._build_content()]

        # Load email
        self.app.page.run_task(self._load_email)

    def _build_content(self) -> ft.Control:
        """Build page content."""
        return ft.Container(
            content=ft.Column(
                [
                    self.loading,
                    self.content_area,
                ],
                expand=True,
                scroll=ft.ScrollMode.AUTO,
            ),
            padding=24,
            expand=True,
        )

    async def _load_email(self) -> None:
        """Load email content."""
        self.loading.visible = True
        self.app.page.update()

        try:
            async with self.app.get_session() as session:
                email_service = EmailService(session)

                # Get email
                self.email = await email_service.get_email(self.email_id)

                if not self.email:
                    self.app.show_snackbar("Email not found", error=True)
                    self._go_back(None)
                    return

                # Mark as read
                if not self.email.is_read:
                    await email_service.mark_as_read(self.email_id)

            # Update UI
            self.title_text.value = self.email.subject[:50] + (
                "..." if len(self.email.subject) > 50 else ""
            )

            self.star_button.icon = (
                ft.Icons.STAR if self.email.is_starred else ft.Icons.STAR_BORDER
            )
            self.star_button.icon_color = (
                ft.Colors.AMBER if self.email.is_starred else None
            )

            # Build content
            self.content_area.content = self._build_email_content()

        except Exception as ex:
            self.app.show_snackbar(f"Error: {ex}", error=True)
        finally:
            self.loading.visible = False
            self.app.page.update()

    def _build_email_content(self) -> ft.Control:
        """Build the email content view."""
        if not self.email:
            return ft.Container()

        # Format date
        date_str = self.email.received_at.strftime("%B %d, %Y at %I:%M %p")

        # Get HTML content and sanitize for WebView
        html_content = self.email.body_html or ""
        if html_content:
            safe_html = sanitize_html_for_webview(html_content)
        else:
            # Fallback to text - wrap in minimal HTML
            safe_html = sanitize_html_for_webview(
                f"<pre>{self.email.body_text or 'No content'}</pre>"
            )

        # Create data URL with base64-encoded HTML
        html_bytes = safe_html.encode("utf-8")
        html_base64 = base64.b64encode(html_bytes).decode("ascii")
        data_url = f"data:text/html;base64,{html_base64}"

        # Create WebView with data URL
        email_webview = WebView(
            url=data_url,
            expand=True,
        )

        return ft.Column(
            [
                # Header
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                self.email.subject,
                                size=24,
                                weight=ft.FontWeight.BOLD,
                            ),
                            ft.Container(height=16),
                            ft.Row(
                                [
                                    ft.CircleAvatar(
                                        content=ft.Text(
                                            (self.email.sender_name or self.email.sender_email)[
                                                0
                                            ].upper()
                                        ),
                                        radius=20,
                                    ),
                                    ft.Container(width=12),
                                    ft.Column(
                                        [
                                            ft.Text(
                                                self.email.sender_name
                                                or self.email.sender_email,
                                                size=14,
                                                weight=ft.FontWeight.BOLD,
                                            ),
                                            ft.Text(
                                                self.email.sender_email,
                                                size=12,
                                                color=ft.Colors.ON_SURFACE_VARIANT,
                                            ),
                                        ],
                                        spacing=2,
                                    ),
                                    ft.Container(expand=True),
                                    ft.Text(
                                        date_str,
                                        size=12,
                                        color=ft.Colors.ON_SURFACE_VARIANT,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    padding=ft.Padding(bottom=24),
                ),
                ft.Divider(),
                ft.Container(height=16),
                # Email body - render in WebView
                ft.Container(
                    content=email_webview,
                    expand=True,
                    height=600,
                ),
            ],
        )

    def _go_back(self, e: Optional[ft.ControlEvent]) -> None:
        """Go back to email list."""
        if self.email:
            self.app.navigate(f"/newsletter/{self.email.newsletter_id}")
        else:
            self.app.navigate("/home")

    async def _toggle_star(self, e: ft.ControlEvent) -> None:
        """Toggle star status."""
        try:
            async with self.app.get_session() as session:
                email_service = EmailService(session)
                self.email = await email_service.toggle_starred(self.email_id)

            if self.email:
                self.star_button.icon = (
                    ft.Icons.STAR if self.email.is_starred else ft.Icons.STAR_BORDER
                )
                self.star_button.icon_color = (
                    ft.Colors.AMBER if self.email.is_starred else None
                )
                self.app.page.update()
        except Exception as ex:
            self.app.show_snackbar(f"Error: {ex}", error=True)

    async def _mark_unread(self, e: ft.ControlEvent) -> None:
        """Mark email as unread and go back."""
        try:
            async with self.app.get_session() as session:
                email_service = EmailService(session)
                await email_service.mark_as_unread(self.email_id)

            self.app.show_snackbar("Marked as unread")
            self._go_back(None)
        except Exception as ex:
            self.app.show_snackbar(f"Error: {ex}", error=True)

    async def _archive(self, e: ft.ControlEvent) -> None:
        """Archive email and go back."""
        try:
            async with self.app.get_session() as session:
                email_service = EmailService(session)
                await email_service.archive_email(self.email_id)

            self.app.show_snackbar("Email archived")
            self._go_back(None)
        except Exception as ex:
            self.app.show_snackbar(f"Error: {ex}", error=True)
