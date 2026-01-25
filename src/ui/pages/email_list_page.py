"""Email list page for a newsletter with sidebar navigation."""

import asyncio
import math
from typing import TYPE_CHECKING

import flet as ft

from src.services.email_service import EmailService
from src.services.fetch_queue_service import FetchPriority
from src.services.newsletter_service import NewsletterService
from src.ui.components import EmailListItem, Sidebar
from src.ui.components.dialogs import EditNewsletterDialog
from src.ui.themes import BorderRadius, Colors, Spacing, Typography, get_colors

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
        colors=None,
    ):
        self.filter_key = filter_key
        self._on_click = on_click
        self._colors = colors or Colors.Light

        super().__init__(
            content=ft.Text(
                label,
                size=Typography.BODY_SMALL_SIZE,
                weight=ft.FontWeight.W_500 if is_active else ft.FontWeight.W_400,
                color=self._colors.ACCENT if is_active else self._colors.TEXT_SECONDARY,
            ),
            padding=ft.padding.symmetric(horizontal=Spacing.SM, vertical=Spacing.XS),
            border_radius=BorderRadius.SM,
            bgcolor=self._colors.ACCENT_MUTED if is_active else None,
            on_click=self._handle_click,
            on_hover=self._on_hover if not is_active else None,
        )

    def _handle_click(self, e: ft.ControlEvent) -> None:
        if self._on_click:
            self._on_click(self.filter_key)

    def _on_hover(self, e: ft.HoverEvent) -> None:
        self.bgcolor = self._colors.HOVER if e.data == "true" else None
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

        # Get theme-aware colors
        self.colors = get_colors(self.app.page)

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
            color=self.colors.ACCENT,
        )

        self.title_text = ft.Text(
            "Loading...",
            size=Typography.H2_SIZE,
            weight=ft.FontWeight.W_600,
            color=self.colors.TEXT_PRIMARY,
        )

        self.sidebar = Sidebar(
            current_route=f"/newsletter/{newsletter_id}",
            newsletters=[],
            on_navigate=self._handle_navigate,
            page=self.app.page,
        )

        # Empty state elements (stored as instance vars for dynamic updates)
        self.empty_state_heading = ft.Text(
            "No emails yet",
            size=Typography.H4_SIZE,
            weight=ft.FontWeight.W_500,
            color=self.colors.TEXT_SECONDARY,
        )
        self.empty_state_subheading = ft.Text(
            "Fetch emails to get started",
            size=Typography.BODY_SIZE,
            color=self.colors.TEXT_TERTIARY,
        )
        self.empty_state_fetch_button = ft.ElevatedButton(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.REFRESH, size=18, color="#FFFFFF"),
                    ft.Container(width=Spacing.XS),
                    ft.Text("Fetch Now"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            bgcolor=self.colors.ACCENT,
            color="#FFFFFF",
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
            ),
            on_click=lambda e: self.app.page.run_task(self._on_refresh, e),
        )

        self.empty_state = ft.Container(
            content=ft.Column(
                [
                    ft.Icon(
                        ft.Icons.INBOX_OUTLINED,
                        size=48,
                        color=self.colors.TEXT_TERTIARY,
                    ),
                    ft.Container(height=Spacing.MD),
                    self.empty_state_heading,
                    ft.Container(height=Spacing.XS),
                    self.empty_state_subheading,
                    ft.Container(height=Spacing.LG),
                    self.empty_state_fetch_button,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            expand=True,
            alignment=ft.alignment.Alignment.CENTER,
            visible=False,
        )

        self.filter_tabs = ft.Row(
            [
                FilterTab("All", "all", is_active=True, on_click=self._on_filter_change, colors=self.colors),
                FilterTab("Unread", "unread", on_click=self._on_filter_change, colors=self.colors),
                FilterTab("Starred", "starred", on_click=self._on_filter_change, colors=self.colors),
            ],
            spacing=Spacing.XXS,
        )

        # Pagination controls
        self.prev_button = ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            icon_color=self.colors.TEXT_DISABLED,
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
            icon_color=self.colors.TEXT_DISABLED,
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
            color=self.colors.TEXT_SECONDARY,
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
        c = self.colors  # Shorthand for readability
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
                                            icon_color=c.TEXT_SECONDARY,
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
                                        ft.IconButton(
                                            icon=ft.Icons.EDIT_OUTLINED,
                                            icon_color=c.TEXT_TERTIARY,
                                            icon_size=18,
                                            tooltip="Edit newsletter",
                                            style=ft.ButtonStyle(
                                                shape=ft.RoundedRectangleBorder(
                                                    radius=BorderRadius.SM
                                                ),
                                            ),
                                            on_click=lambda _: self._show_edit_dialog(),
                                        ),
                                        ft.Container(expand=True),
                                        self.loading,
                                        ft.Container(width=Spacing.SM),
                                        ft.IconButton(
                                            icon=ft.Icons.REFRESH,
                                            icon_color=c.TEXT_SECONDARY,
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
                            ft.Divider(height=1, color=c.BORDER_SUBTLE),
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
                    bgcolor=c.BG_SECONDARY,
                ),
            ],
            expand=True,
            spacing=0,
        )

    def _handle_navigate(self, route: str) -> None:
        """Handle navigation from sidebar."""
        self.app.navigate(route)

    def _update_empty_state_content(self) -> None:
        """Update empty state content based on current filter."""
        if self.current_filter == "starred":
            self.empty_state_heading.value = "No starred emails"
            self.empty_state_subheading.value = "Star emails to see them here"
            self.empty_state_fetch_button.visible = False
        elif self.current_filter == "unread":
            self.empty_state_heading.value = "No unread emails"
            self.empty_state_subheading.value = "All caught up!"
            self.empty_state_fetch_button.visible = False
        else:  # "all"
            self.empty_state_heading.value = "No emails yet"
            self.empty_state_subheading.value = "Fetch emails to get started"
            self.empty_state_fetch_button.visible = True

    def _on_filter_change(self, filter_key: str) -> None:
        """Handle filter tab change."""
        self.current_filter = filter_key
        # Reset to first page when filter changes
        self.current_page = 1
        # Update tab states
        c = self.colors
        for tab in self.filter_tabs.controls:
            is_active = tab.filter_key == filter_key
            tab.content.weight = (
                ft.FontWeight.W_500 if is_active else ft.FontWeight.W_400
            )
            tab.content.color = (
                c.ACCENT if is_active else c.TEXT_SECONDARY
            )
            tab.bgcolor = c.ACCENT_MUTED if is_active else None
            tab.on_hover = None if is_active else tab._on_hover
        self.filter_tabs.update()
        # Update empty state content for new filter
        self._update_empty_state_content()
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
                self._update_empty_state_content()
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
            colors=self.colors,
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

    def _show_edit_dialog(self) -> None:
        """Show dialog to edit the current newsletter."""

        async def save_changes(e) -> None:
            try:
                values = dialog.get_values()
                name = (values["name"] or "").strip()

                if not name:
                    self.app.show_snackbar("Name is required", error=True)
                    return

                async with self.app.get_session() as session:
                    service = NewsletterService(session=session)
                    await service.update_newsletter(
                        newsletter_id=self.newsletter.id,
                        name=name,
                        auto_fetch=values["auto_fetch"],
                        fetch_interval=values["interval"],
                        color=values.get("color"),
                        color_secondary=values.get("color_secondary"),
                    )

                dialog.open = False
                self.app.page.update()
                self.app.show_snackbar("Newsletter updated")

                # Update title
                self.title_text.value = name
                # Reload data to update sidebar with new colors
                await self._load_data()
            except Exception as ex:
                self.app.show_snackbar(f"Error: {ex}", error=True)

        def close_dialog(_):
            dialog.open = False
            self.app.page.update()

        dialog = EditNewsletterDialog(
            newsletter=self.newsletter,
            on_save=lambda e: self.app.page.run_task(save_changes, e),
            on_cancel=close_dialog,
        )

        self.app.page.show_dialog(dialog)

    def _update_pagination_controls(self) -> None:
        """Update pagination controls based on current state."""
        c = self.colors
        # Update page indicator
        self.page_indicator.value = f"Page {self.current_page} of {self.total_pages}"

        # Update prev button
        can_go_prev = self.current_page > 1
        self.prev_button.disabled = not can_go_prev
        self.prev_button.icon_color = (
            c.TEXT_SECONDARY if can_go_prev else c.TEXT_DISABLED
        )

        # Update next button
        can_go_next = self.current_page < self.total_pages
        self.next_button.disabled = not can_go_next
        self.next_button.icon_color = (
            c.TEXT_SECONDARY if can_go_next else c.TEXT_DISABLED
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
