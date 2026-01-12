"""Email list page for a newsletter with sidebar navigation."""

import asyncio
import math
from typing import TYPE_CHECKING

import flet as ft

from src.services.email_service import EmailService
from src.services.fetch_queue_service import FetchPriority
from src.services.newsletter_service import NewsletterService
from src.ui.components import EmailListItem, Sidebar
from src.ui.themes import BorderRadius, Colors, Spacing, Typography

if TYPE_CHECKING:
    from src.app import NewsletterApp


class FilterTab(ft.Container):
    """Filter tab button component."""

    def __init__(
        self,
        label: str,
        filter_key: str,
        is_active: bool = False,
        on_click=None,
    ):
        self.filter_key = filter_key
        self._on_click = on_click

        super().__init__(
            content=ft.Text(
                label,
                size=Typography.BODY_SMALL_SIZE,
                weight=ft.FontWeight.W_500 if is_active else ft.FontWeight.W_400,
                color=Colors.Light.ACCENT if is_active else Colors.Light.TEXT_SECONDARY,
            ),
            padding=ft.padding.symmetric(horizontal=Spacing.SM, vertical=Spacing.XS),
            border_radius=BorderRadius.SM,
            bgcolor=Colors.Light.ACCENT_MUTED if is_active else None,
            on_click=self._handle_click,
            on_hover=self._on_hover if not is_active else None,
        )

    def _handle_click(self, e: ft.ControlEvent) -> None:
        if self._on_click:
            self._on_click(self.filter_key)

    def _on_hover(self, e: ft.HoverEvent) -> None:
        self.bgcolor = Colors.Light.HOVER if e.data == "true" else None
        self.update()


class EmailListPage(ft.View):
    """Page showing emails for a newsletter with sidebar."""

    def __init__(self, app: "NewsletterApp", newsletter_id: int):
        super().__init__(route=f"/newsletter/{newsletter_id}", padding=0, spacing=0)
        self.app = app
        self.newsletter_id = newsletter_id
        self.newsletter = None
        self.newsletters = []
        self.current_filter = "all"  # all, unread, starred

        # Pagination state
        self.current_page = 1
        self.page_size = 20
        self.total_emails = 0
        self.total_pages = 0

        self.emails_list = ft.ListView(
            expand=True,
            spacing=0,
            padding=0,
        )

        self.loading = ft.ProgressRing(
            visible=False,
            width=20,
            height=20,
            stroke_width=2,
            color=Colors.Light.ACCENT,
        )

        self.title_text = ft.Text(
            "Loading...",
            size=Typography.H2_SIZE,
            weight=ft.FontWeight.W_600,
            color=Colors.Light.TEXT_PRIMARY,
        )

        self.sidebar = Sidebar(
            current_route=f"/newsletter/{newsletter_id}",
            newsletters=[],
            on_navigate=self._handle_navigate,
        )

        self.empty_state = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.INBOX_OUTLINED,
                        size=48,
                        color=Colors.Light.TEXT_TERTIARY,
                    ),
                    ft.Container(height=Spacing.MD),
                    ft.Text(
                        "No emails yet",
                        size=Typography.H4_SIZE,
                        weight=ft.FontWeight.W_500,
                        color=Colors.Light.TEXT_SECONDARY,
                    ),
                    ft.Container(height=Spacing.XS),
                    ft.Text(
                        "Fetch emails to get started",
                        size=Typography.BODY_SIZE,
                        color=Colors.Light.TEXT_TERTIARY,
                    ),
                    ft.Container(height=Spacing.LG),
                    ft.ElevatedButton(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.REFRESH, size=18, color="#FFFFFF"),
                                ft.Container(width=Spacing.XS),
                                ft.Text("Fetch Now"),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                        ),
                        bgcolor=Colors.Light.ACCENT,
                        color="#FFFFFF",
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
                        ),
                        on_click=lambda e: self.app.page.run_task(self._on_refresh, e),
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            alignment=ft.alignment.Alignment.CENTER,
            visible=False,
        )

        self.filter_tabs = ft.Row(
            [
                FilterTab("All", "all", is_active=True, on_click=self._on_filter_change),
                FilterTab("Unread", "unread", on_click=self._on_filter_change),
                FilterTab("Starred", "starred", on_click=self._on_filter_change),
            ],
            spacing=Spacing.XXS,
        )

        # Pagination controls
        self.prev_button = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            icon_color=Colors.Light.TEXT_DISABLED,
            icon_size=20,
            disabled=True,
            tooltip="Previous page",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
            ),
            on_click=lambda _: self._on_prev_page(),
        )

        self.next_button = ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            icon_color=Colors.Light.TEXT_DISABLED,
            icon_size=20,
            disabled=True,
            tooltip="Next page",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
            ),
            on_click=lambda _: self._on_next_page(),
        )

        self.page_indicator = ft.Text(
            "Page 1 of 1",
            size=Typography.BODY_SMALL_SIZE,
            color=Colors.Light.TEXT_SECONDARY,
        )

        self.pagination_controls = ft.Container(
            content=ft.Row(
                [
                    self.prev_button,
                    ft.Container(width=Spacing.SM),
                    self.page_indicator,
                    ft.Container(width=Spacing.SM),
                    self.next_button,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(vertical=Spacing.MD),
            visible=False,  # Hidden until data loads
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
                            # Header
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
                                        self.title_text,
                                        ft.Container(expand=True),
                                        self.loading,
                                        ft.Container(width=Spacing.SM),
                                        ft.IconButton(
                                            icon=ft.Icons.REFRESH,
                                            icon_color=Colors.Light.TEXT_SECONDARY,
                                            icon_size=20,
                                            tooltip="Fetch new emails",
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(
                                                    radius=BorderRadius.SM
                                                ),
                                            ),
                                            on_click=lambda e: self.app.page.run_task(
                                                self._on_refresh, e
                                            ),
                                        ),
                                    ],
                                ),
                                padding=ft.padding.only(bottom=Spacing.MD),
                            ),
                            # Filter tabs
                            ft.Container(
                                content=self.filter_tabs,
                                padding=ft.padding.only(bottom=Spacing.MD),
                            ),
                            # Divider
                            ft.Divider(height=1, color=Colors.Light.BORDER_SUBTLE),
                            # Email list
                            ft.Container(
                                content=ft.Stack(
                                    [
                                        self.emails_list,
                                        self.empty_state,
                                    ],
                                    expand=True,
                                ),
                                expand=True,
                            ),
                            # Pagination controls
                            self.pagination_controls,
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

    def _handle_navigate(self, route: str) -> None:
        """Handle navigation from sidebar."""
        self.app.navigate(route)

    def _on_filter_change(self, filter_key: str) -> None:
        """Handle filter tab change."""
        self.current_filter = filter_key
        # Reset to first page when filter changes
        self.current_page = 1
        # Update tab states
        for tab in self.filter_tabs.controls:
            is_active = tab.filter_key == filter_key
            tab.content.weight = (
                ft.FontWeight.W_500 if is_active else ft.FontWeight.W_400
            )
            tab.content.color = (
                Colors.Light.ACCENT if is_active else Colors.Light.TEXT_SECONDARY
            )
            tab.bgcolor = Colors.Light.ACCENT_MUTED if is_active else None
            tab.on_hover = None if is_active else tab._on_hover
        self.filter_tabs.update()
        # Reload with filter
        self.app.page.run_task(self._load_data)

    async def _load_data(self) -> None:
        """Load newsletter and emails."""
        self.loading.visible = True
        self.app.page.update()

        try:
            async with self.app.get_session() as session:
                # Load all newsletters for sidebar
                newsletter_service = NewsletterService(session=session)
                self.newsletters = await newsletter_service.get_all_newsletters()

                # Load current newsletter
                self.newsletter = await newsletter_service.get_newsletter(
                    self.newsletter_id
                )

                if not self.newsletter:
                    self.app.show_snackbar("Newsletter not found", error=True)
                    self.app.navigate("/home")
                    return

                self.title_text.value = self.newsletter.name

                # Load emails with filter and pagination
                email_service = EmailService(session)
                offset = (self.current_page - 1) * self.page_size

                # Determine filter flags
                unread_only = self.current_filter == "unread"
                starred_only = self.current_filter == "starred"

                # Get total count for pagination
                self.total_emails = await email_service.get_filtered_count(
                    self.newsletter_id,
                    unread_only=unread_only,
                    starred_only=starred_only,
                )
                self.total_pages = max(1, math.ceil(self.total_emails / self.page_size))

                # Ensure current page is valid
                if self.current_page > self.total_pages:
                    self.current_page = self.total_pages
                    offset = (self.current_page - 1) * self.page_size

                # Fetch emails for current page
                emails = await email_service.get_emails_for_newsletter(
                    self.newsletter_id,
                    limit=self.page_size,
                    offset=offset,
                    unread_only=unread_only,
                    starred_only=starred_only,
                )

                # Extract email data while still in session context
                email_data = []
                for email in emails:
                    email_data.append(
                        {
                            "id": email.id,
                            "subject": email.subject,
                            "sender_name": email.sender_name,
                            "sender_email": email.sender_email,
                            "snippet": email.snippet,
                            "received_at": email.received_at,
                            "is_read": email.is_read,
                            "is_starred": email.is_starred,
                        }
                    )

            # Update sidebar
            self.sidebar.update_newsletters(self.newsletters)
            self.sidebar.update_route(f"/newsletter/{self.newsletter_id}")

            # Update email list
            self.emails_list.controls.clear()

            if email_data:
                self.empty_state.visible = False
                for data in email_data:
                    item = self._create_email_item(data)
                    self.emails_list.controls.append(item)
            else:
                self.empty_state.visible = True

            # Update pagination controls
            self._update_pagination_controls()

        except Exception as ex:
            self.app.show_snackbar(f"Error: {ex}", error=True)
        finally:
            self.loading.visible = False
            self.app.page.update()

    def _create_email_item(self, email: dict) -> ft.Control:
        """Create an email list item."""
        email_id = email["id"]
        return EmailListItem(
            subject=email["subject"] or "(No subject)",
            sender=email["sender_name"] or email["sender_email"],
            snippet=email["snippet"] or "",
            received_at=email["received_at"],
            is_read=email["is_read"],
            is_starred=email["is_starred"],
            on_click=lambda _, eid=email_id: self.app.navigate(f"/email/{eid}"),
            on_star=lambda _, eid=email_id: self.app.page.run_task(
                self._toggle_star, eid
            ),
        )

    async def _on_refresh(self, e: ft.ControlEvent) -> None:
        """Fetch new emails."""
        if not self.app.fetch_queue_service:
            return

        await self.app.fetch_queue_service.queue_fetch(
            self.newsletter_id, FetchPriority.HIGH
        )
        self.app.show_snackbar("Fetching new emails...")

        # Wait a bit and reload
        await asyncio.sleep(2)
        await self._load_data()

    async def _toggle_star(self, email_id: int) -> None:
        """Toggle email starred status."""
        try:
            async with self.app.get_session() as session:
                email_service = EmailService(session)
                await email_service.toggle_starred(email_id)
            await self._load_data()
        except Exception as ex:
            self.app.show_snackbar(f"Error: {ex}", error=True)

    def _update_pagination_controls(self) -> None:
        """Update pagination controls based on current state."""
        # Update page indicator
        self.page_indicator.value = f"Page {self.current_page} of {self.total_pages}"

        # Update prev button
        can_go_prev = self.current_page > 1
        self.prev_button.disabled = not can_go_prev
        self.prev_button.icon_color = (
            Colors.Light.TEXT_SECONDARY if can_go_prev else Colors.Light.TEXT_DISABLED
        )

        # Update next button
        can_go_next = self.current_page < self.total_pages
        self.next_button.disabled = not can_go_next
        self.next_button.icon_color = (
            Colors.Light.TEXT_SECONDARY if can_go_next else Colors.Light.TEXT_DISABLED
        )

        # Show pagination only if there are emails
        self.pagination_controls.visible = self.total_emails > 0

    def _on_prev_page(self) -> None:
        """Navigate to previous page."""
        if self.current_page > 1:
            self.current_page -= 1
            self.app.page.run_task(self._load_data)

    def _on_next_page(self) -> None:
        """Navigate to next page."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.app.page.run_task(self._load_data)
