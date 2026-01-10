"""Email reader page for viewing email content with sophisticated styling."""

import base64
from typing import TYPE_CHECKING, Optional

import flet as ft
from flet_webview import WebView

from src.services.email_service import EmailService
from src.services.newsletter_service import NewsletterService
from src.ui.components import Sidebar
from src.ui.themes import BorderRadius, Colors, Spacing, Typography
from src.utils.html_sanitizer import sanitize_html_for_webview

if TYPE_CHECKING:
    from src.app import NewsletterApp


class EmailReaderPage(ft.View):
    """Page for reading email content with sidebar."""

    def __init__(self, app: "NewsletterApp", email_id: int):
        super().__init__(route=f"/email/{email_id}", padding=0, spacing=0)
        self.app = app
        self.email_id = email_id
        self.email = None
        self.newsletters = []

        self.content_area = ft.Container(expand=True)
        self.loading = ft.ProgressRing(
            visible=False,
            width=20,
            height=20,
            stroke_width=2,
            color=Colors.Light.ACCENT,
        )
        self.subject_text = ft.Text(
            "Loading...",
            size=Typography.H3_SIZE,
            weight=ft.FontWeight.W_600,
            color=Colors.Light.TEXT_PRIMARY,
        )

        self.star_button = ft.IconButton(
            icon=ft.Icons.STAR_OUTLINE,
            icon_color=Colors.Light.STAR_INACTIVE,
            icon_size=20,
            tooltip="Star",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
            ),
            on_click=lambda e: self.app.page.run_task(self._toggle_star, e),
        )

        self.sidebar = Sidebar(
            current_route=f"/email/{email_id}",
            newsletters=[],
            on_navigate=self._handle_navigate,
        )

        self.controls = [self._build_content()]

        # Load email
        self.app.page.run_task(self._load_email)

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
                            # Action bar
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
                                            on_click=self._go_back,
                                        ),
                                        ft.Container(expand=True),
                                        self.loading,
                                        ft.Container(width=Spacing.XS),
                                        self.star_button,
                                        ft.IconButton(
                                            icon=ft.Icons.MARK_EMAIL_UNREAD,
                                            icon_color=Colors.Light.TEXT_SECONDARY,
                                            icon_size=20,
                                            tooltip="Mark as unread",
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(
                                                    radius=BorderRadius.SM
                                                ),
                                            ),
                                            on_click=lambda e: self.app.page.run_task(
                                                self._mark_unread, e
                                            ),
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.ARCHIVE_OUTLINED,
                                            icon_color=Colors.Light.TEXT_SECONDARY,
                                            icon_size=20,
                                            tooltip="Archive",
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(
                                                    radius=BorderRadius.SM
                                                ),
                                            ),
                                            on_click=lambda e: self.app.page.run_task(
                                                self._archive, e
                                            ),
                                        ),
                                    ],
                                ),
                                padding=ft.padding.only(bottom=Spacing.MD),
                                border=ft.border.only(
                                    bottom=ft.BorderSide(1, Colors.Light.BORDER_SUBTLE)
                                ),
                            ),
                            # Email content (scrollable)
                            ft.Container(
                                content=self.content_area,
                                expand=True,
                                padding=ft.padding.only(top=Spacing.LG),
                            ),
                        ],
                        expand=True,
                    ),
                    padding=Spacing.LG,
                    expand=True,
                    bgcolor=Colors.Light.BG_PRIMARY,
                ),
            ],
            expand=True,
            spacing=0,
        )

    def _handle_navigate(self, route: str) -> None:
        """Handle navigation from sidebar."""
        self.app.navigate(route)

    async def _load_email(self) -> None:
        """Load email content."""
        self.loading.visible = True
        self.app.page.update()

        try:
            async with self.app.get_session() as session:
                email_service = EmailService(session)

                # Load newsletters for sidebar
                newsletter_service = NewsletterService(session=session)
                self.newsletters = await newsletter_service.get_all_newsletters()

                # Get email
                self.email = await email_service.get_email(self.email_id)

                if not self.email:
                    self.app.show_snackbar("Email not found", error=True)
                    self._go_back(None)
                    return

                # Mark as read
                if not self.email.is_read:
                    await email_service.mark_as_read(self.email_id)

            # Update sidebar
            self.sidebar.update_newsletters(self.newsletters)

            # Update star button
            self.star_button.icon = (
                ft.Icons.STAR if self.email.is_starred else ft.Icons.STAR_OUTLINE
            )
            self.star_button.icon_color = (
                Colors.Light.STAR_ACTIVE
                if self.email.is_starred
                else Colors.Light.STAR_INACTIVE
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
                f"<pre style='font-family: system-ui, sans-serif; white-space: pre-wrap;'>{self.email.body_text or 'No content'}</pre>"
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
                # Subject
                ft.Text(
                    self.email.subject,
                    size=Typography.H2_SIZE,
                    weight=ft.FontWeight.W_600,
                    color=Colors.Light.TEXT_PRIMARY,
                ),
                ft.Container(height=Spacing.LG),
                # Sender info
                ft.Row(
                    [
                        ft.CircleAvatar(
                            content=ft.Text(
                                (
                                    self.email.sender_name or self.email.sender_email
                                )[0].upper(),
                                size=Typography.BODY_SIZE,
                                weight=ft.FontWeight.W_500,
                            ),
                            radius=20,
                            bgcolor=Colors.Light.BG_TERTIARY,
                            color=Colors.Light.TEXT_PRIMARY,
                        ),
                        ft.Container(width=Spacing.SM),
                        ft.Column(
                            [
                                ft.Text(
                                    self.email.sender_name or self.email.sender_email,
                                    size=Typography.BODY_SIZE,
                                    weight=ft.FontWeight.W_500,
                                    color=Colors.Light.TEXT_PRIMARY,
                                ),
                                ft.Text(
                                    self.email.sender_email,
                                    size=Typography.CAPTION_SIZE,
                                    color=Colors.Light.TEXT_TERTIARY,
                                ),
                            ],
                            spacing=2,
                        ),
                        ft.Container(expand=True),
                        ft.Text(
                            date_str,
                            size=Typography.CAPTION_SIZE,
                            color=Colors.Light.TEXT_TERTIARY,
                            font_family="monospace",
                        ),
                    ],
                ),
                ft.Container(height=Spacing.LG),
                # Divider
                ft.Divider(height=1, color=Colors.Light.BORDER_SUBTLE),
                ft.Container(height=Spacing.MD),
                # Email body - render in WebView
                ft.Container(
                    content=email_webview,
                    expand=True,
                    height=600,
                    border_radius=BorderRadius.MD,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                ),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
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
                    ft.Icons.STAR if self.email.is_starred else ft.Icons.STAR_OUTLINE
                )
                self.star_button.icon_color = (
                    Colors.Light.STAR_ACTIVE
                    if self.email.is_starred
                    else Colors.Light.STAR_INACTIVE
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
