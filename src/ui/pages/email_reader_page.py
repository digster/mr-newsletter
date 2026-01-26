"""Email reader page for viewing email content with sophisticated styling."""

import base64
import logging
from typing import TYPE_CHECKING

import flet as ft
from flet_webview import WebView

from src.repositories.user_settings_repository import UserSettingsRepository
from src.services.email_service import EmailService
from src.services.newsletter_service import NewsletterService
from src.ui.components import Sidebar, SummaryCard
from src.ui.themes import BorderRadius, Spacing, Typography, get_colors
from src.utils.html_sanitizer import sanitize_html_for_webview

if TYPE_CHECKING:
    from src.app import NewsletterApp

logger = logging.getLogger(__name__)


class EmailReaderPage(ft.View):
    """Page for reading email content with sidebar."""

    def __init__(self, app: "NewsletterApp", email_id: int):
        super().__init__(route=f"/email/{email_id}", padding=0, spacing=0)
        self.app = app
        self.email_id = email_id
        self.email = None
        self.newsletters = []
        self._user_settings = None
        self._llm_enabled = False

        # Get theme-aware colors
        self.colors = get_colors(self.app.page)

        self.content_area = ft.Container(expand=True)
        self.loading = ft.ProgressRing(
            visible=False,
            width=20,
            height=20,
            stroke_width=2,
            color=self.colors.ACCENT,
        )
        self.subject_text = ft.Text(
            "Loading...",
            size=Typography.H3_SIZE,
            weight=ft.FontWeight.W_600,
            color=self.colors.TEXT_PRIMARY,
        )

        self.star_button = ft.IconButton(
            icon=ft.Icons.STAR_OUTLINE,
            icon_color=self.colors.STAR_INACTIVE,
            icon_size=20,
            tooltip="Star",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
            ),
            on_click=lambda e: self.app.page.run_task(self._toggle_star, e),
        )

        # AI Summarize button
        self.summarize_button = ft.IconButton(
            icon=ft.Icons.AUTO_AWESOME,
            icon_color=self.colors.TEXT_SECONDARY,
            icon_size=20,
            tooltip="Summarize with AI",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
            ),
            on_click=lambda e: self.app.page.run_task(self._summarize_email, e),
            visible=False,  # Will be shown if LLM is enabled
        )

        # Summary card
        self.summary_card = SummaryCard(
            colors=self.colors,
            on_generate=lambda e: self.app.page.run_task(self._summarize_email, e),
            on_regenerate=lambda e: self.app.page.run_task(self._regenerate_summary, e),
            is_enabled=False,
        )

        # Archive/Unarchive button (stored for dynamic updates)
        self.archive_button = ft.IconButton(
            icon=ft.Icons.ARCHIVE_OUTLINED,
            icon_color=self.colors.TEXT_SECONDARY,
            icon_size=20,
            tooltip="Archive",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
            ),
            on_click=lambda e: self.app.page.run_task(self._toggle_archive, e),
        )

        self.sidebar = Sidebar(
            current_route=f"/email/{email_id}",
            newsletters=[],
            on_navigate=self._handle_navigate,
            page=self.app.page,
        )

        self.controls = [self._build_content()]

        # Load email
        self.app.page.run_task(self._load_email)

    def _build_content(self) -> ft.Control:
        """Build page content with sidebar."""
        c = self.colors  # Shorthand for readability
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
                                            icon_color=c.TEXT_SECONDARY,
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
                                        self.summarize_button,
                                        ft.IconButton(
                                            icon=ft.Icons.MARK_EMAIL_UNREAD,
                                            icon_color=c.TEXT_SECONDARY,
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
                                        self.archive_button,
                                    ],
                                ),
                                padding=ft.padding.only(bottom=Spacing.MD),
                                border=ft.border.only(
                                    bottom=ft.BorderSide(1, c.BORDER_SUBTLE)
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
                    bgcolor=c.BG_PRIMARY,
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

                # Load user settings for LLM
                settings_repo = UserSettingsRepository(session)
                self._user_settings = await settings_repo.get_settings()
                self._llm_enabled = getattr(self._user_settings, "llm_enabled", False)

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
                self.colors.STAR_ACTIVE
                if self.email.is_starred
                else self.colors.STAR_INACTIVE
            )

            # Update archive button based on archived status
            if self.email.is_archived:
                self.archive_button.icon = ft.Icons.UNARCHIVE_OUTLINED
                self.archive_button.tooltip = "Unarchive"
            else:
                self.archive_button.icon = ft.Icons.ARCHIVE_OUTLINED
                self.archive_button.tooltip = "Archive"

            # Update summarize button visibility
            self.summarize_button.visible = self._llm_enabled

            # Update summary card (safe - uses _safe_update_content internally)
            self.summary_card.set_enabled(self._llm_enabled)
            if self.email.summary:
                self.summary_card.set_summary(
                    summary=self.email.summary,
                    model=self.email.summary_model,
                    summarized_at=self.email.summarized_at,
                )

            # Build content
            self.content_area.content = self._build_email_content()

        except Exception as ex:
            logger.error(f"Error loading email: {ex}", exc_info=True)
            self.app.show_snackbar(f"Error: {ex}", error=True)
        finally:
            self.loading.visible = False
            self.app.page.update()

    def _build_email_content(self) -> ft.Control:
        """Build the email content view."""
        if not self.email:
            return ft.Container()

        c = self.colors  # Shorthand for readability

        # Format date
        date_str = self.email.received_at.strftime("%B %d, %Y at %I:%M %p")

        # Get HTML content and sanitize for WebView
        html_content = self.email.body_html or ""
        if html_content:
            safe_html = sanitize_html_for_webview(html_content)
        else:
            # Fallback to text - wrap in minimal HTML
            text_content = self.email.body_text or "No content"
            pre_style = "font-family: system-ui, sans-serif; white-space: pre-wrap;"
            safe_html = sanitize_html_for_webview(
                f"<pre style='{pre_style}'>{text_content}</pre>"
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
                    color=c.TEXT_PRIMARY,
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
                            bgcolor=c.BG_TERTIARY,
                            color=c.TEXT_PRIMARY,
                        ),
                        ft.Container(width=Spacing.SM),
                        ft.Column(
                            [
                                ft.Text(
                                    self.email.sender_name or self.email.sender_email,
                                    size=Typography.BODY_SIZE,
                                    weight=ft.FontWeight.W_500,
                                    color=c.TEXT_PRIMARY,
                                ),
                                ft.Text(
                                    self.email.sender_email,
                                    size=Typography.CAPTION_SIZE,
                                    color=c.TEXT_TERTIARY,
                                ),
                            ],
                            spacing=2,
                        ),
                        ft.Container(expand=True),
                        ft.Text(
                            date_str,
                            size=Typography.CAPTION_SIZE,
                            color=c.TEXT_TERTIARY,
                            font_family="monospace",
                        ),
                    ],
                ),
                ft.Container(height=Spacing.MD),
                # AI Summary card (between sender info and divider)
                self.summary_card,
                ft.Container(height=Spacing.MD),
                # Divider
                ft.Divider(height=1, color=c.BORDER_SUBTLE),
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

    def _go_back(self, e: ft.ControlEvent | None) -> None:
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
                    self.colors.STAR_ACTIVE
                    if self.email.is_starred
                    else self.colors.STAR_INACTIVE
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

    async def _toggle_archive(self, e: ft.ControlEvent) -> None:
        """Toggle archive status and go back."""
        try:
            async with self.app.get_session() as session:
                email_service = EmailService(session)
                if self.email.is_archived:
                    await email_service.unarchive_email(self.email_id)
                    self.app.show_snackbar("Email unarchived")
                else:
                    await email_service.archive_email(self.email_id)
                    self.app.show_snackbar("Email archived")

            self._go_back(None)
        except Exception as ex:
            self.app.show_snackbar(f"Error: {ex}", error=True)

    async def _summarize_email(self, e: ft.ControlEvent) -> None:
        """Generate AI summary for the email."""
        if not self._llm_enabled:
            self.app.show_snackbar(
                "AI summarization is disabled. Enable it in Settings.", error=True
            )
            return

        # Show loading state
        self.summary_card.set_loading(True)
        self.app.page.update()

        # Variables to store extracted values (session objects become detached after context exits)
        summary = None
        model = None
        summarized_at = None
        error = None

        try:
            async with self.app.get_session() as session:
                # Get fresh user settings
                settings_repo = UserSettingsRepository(session)
                user_settings = await settings_repo.get_settings()

                # Generate summary
                email_service = EmailService(session)
                updated_email, error = await email_service.summarize_email(
                    email_id=self.email_id,
                    user_settings=user_settings,
                )

                if error:
                    self.summary_card.set_loading(False)
                    self.app.page.update()
                    self.app.show_snackbar(error, error=True)
                    return

                # Eagerly extract values INSIDE the session while object is attached
                if updated_email:
                    summary = updated_email.summary
                    model = updated_email.summary_model
                    summarized_at = updated_email.summarized_at
                    logger.info(
                        f"Extracted: summary={'<' + str(len(summary)) + ' chars>' if summary else 'None'}, "
                        f"model={model}"
                    )

            # Now outside session - use the extracted values (not the detached object)
            # Use `is not None` check - empty string "" is falsy but valid!
            if summary is not None:
                self.summary_card.set_summary(
                    summary=summary,
                    model=model,
                    summarized_at=summarized_at,
                )
                self.app.page.update()
            else:
                # Summary was None - show error
                self.summary_card.set_loading(False)
                self.app.page.update()
                self.app.show_snackbar("Failed to generate summary", error=True)

        except Exception as ex:
            self.summary_card.set_loading(False)
            self.app.page.update()
            self.app.show_snackbar(f"Error generating summary: {ex}", error=True)

    async def _regenerate_summary(self, e: ft.ControlEvent) -> None:
        """Clear and regenerate the summary."""
        try:
            async with self.app.get_session() as session:
                email_service = EmailService(session)
                await email_service.clear_email_summary(self.email_id)

            # Clear the summary card
            self.summary_card.clear()
            self.app.page.update()

            # Generate new summary
            await self._summarize_email(e)

        except Exception as ex:
            self.app.show_snackbar(f"Error regenerating summary: {ex}", error=True)
