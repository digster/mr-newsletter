"""Email list item component with clean, scannable design."""

from datetime import date, datetime
from typing import Callable, Optional

import flet as ft

from src.ui.themes import BorderRadius, Colors, Spacing, Typography


class EmailListItem(ft.Container):
    """List item for email display with clear read/unread states."""

    def __init__(
        self,
        subject: str,
        sender: str,
        snippet: str,
        received_at: datetime,
        is_read: bool = False,
        is_starred: bool = False,
        on_click: Optional[Callable] = None,
        on_star: Optional[Callable] = None,
    ):
        self.subject = subject
        self.sender = sender
        self.snippet = snippet
        self.received_at = received_at
        self.is_read = is_read
        self.is_starred = is_starred
        self._on_click = on_click
        self._on_star = on_star

        # Format date based on recency
        self.date_str = self._format_date(received_at)

        super().__init__(
            content=self._build_content(),
            padding=ft.padding.symmetric(horizontal=Spacing.MD, vertical=Spacing.SM),
            border_radius=BorderRadius.SM,
            bgcolor=Colors.Light.BG_SECONDARY if not is_read else Colors.Light.BG_PRIMARY,
            border=ft.border.only(bottom=ft.BorderSide(1, Colors.Light.BORDER_SUBTLE)),
            animate=ft.Animation(100, ft.AnimationCurve.EASE_OUT),
            on_click=self._handle_click,
            on_hover=self._on_hover,
        )

    def _build_content(self) -> ft.Control:
        """Build list item content."""
        return ft.Row(
            [
                # Unread indicator dot
                ft.Container(
                    width=6,
                    height=6,
                    border_radius=BorderRadius.FULL,
                    bgcolor=Colors.Light.UNREAD_DOT if not self.is_read else None,
                ),
                ft.Container(width=Spacing.SM),
                # Star button
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.STAR if self.is_starred else ft.Icons.STAR_OUTLINE,
                        size=18,
                        color=Colors.Light.STAR_ACTIVE
                        if self.is_starred
                        else Colors.Light.STAR_INACTIVE,
                    ),
                    on_click=self._handle_star,
                    padding=Spacing.XXS,
                    border_radius=BorderRadius.SM,
                ),
                ft.Container(width=Spacing.SM),
                # Content area
                ft.Column(
                    [
                        # Subject line
                        ft.Text(
                            self.subject or "(No subject)",
                            size=Typography.BODY_SIZE,
                            weight=ft.FontWeight.W_500
                            if not self.is_read
                            else ft.FontWeight.W_400,
                            color=Colors.Light.TEXT_PRIMARY,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Container(height=Spacing.XXS),
                        # Sender and snippet
                        ft.Row(
                            [
                                ft.Text(
                                    self.sender,
                                    size=Typography.CAPTION_SIZE,
                                    color=Colors.Light.TEXT_SECONDARY,
                                    weight=ft.FontWeight.W_500,
                                ),
                                ft.Text(
                                    " — ",
                                    size=Typography.CAPTION_SIZE,
                                    color=Colors.Light.TEXT_TERTIARY,
                                ),
                                ft.Text(
                                    self.snippet,
                                    size=Typography.CAPTION_SIZE,
                                    color=Colors.Light.TEXT_TERTIARY,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                    expand=True,
                                ),
                            ],
                        ),
                    ],
                    spacing=0,
                    expand=True,
                ),
                ft.Container(width=Spacing.MD),
                # Date - monospace
                ft.Text(
                    self.date_str,
                    size=Typography.CAPTION_SIZE,
                    color=Colors.Light.TEXT_TERTIARY,
                    font_family="monospace",
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _format_date(self, dt: datetime) -> str:
        """Format date based on recency."""
        today = date.today()
        email_date = dt.date()

        if email_date == today:
            return dt.strftime("%H:%M")
        elif (today - email_date).days < 7:
            return dt.strftime("%a")
        elif email_date.year == today.year:
            return dt.strftime("%b %d")
        else:
            return dt.strftime("%b %d, %Y")

    def _handle_click(self, e: ft.ControlEvent) -> None:
        """Handle click event."""
        if self._on_click:
            self._on_click(e)

    def _handle_star(self, e: ft.ControlEvent) -> None:
        """Handle star toggle."""
        e.control.data = "star"  # Mark as star click
        if self._on_star:
            self._on_star(e)

    def _on_hover(self, e: ft.HoverEvent) -> None:
        """Handle hover state."""
        if e.data == "true":
            self.bgcolor = Colors.Light.HOVER
        else:
            self.bgcolor = (
                Colors.Light.BG_SECONDARY
                if not self.is_read
                else Colors.Light.BG_PRIMARY
            )
        self.update()
