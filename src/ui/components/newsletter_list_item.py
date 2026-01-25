"""Newsletter list item component for compact list view."""

from datetime import datetime
from typing import Callable, Optional, Union

import flet as ft

from src.ui.components.gradient_dot import create_gradient_dot
from src.ui.themes import BorderRadius, Colors, Spacing, Typography
from src.ui.utils import format_relative_time


class NewsletterListItem(ft.Container):
    """Compact list row for newsletter display."""

    def __init__(
        self,
        name: str,
        label: str,
        unread_count: int,
        total_count: int,
        last_email_received_at: Optional[datetime] = None,
        color: Optional[str] = None,
        color_secondary: Optional[str] = None,
        on_click: Optional[Callable] = None,
        on_refresh: Optional[Callable] = None,
        colors: Optional[Union[type[Colors.Light], type[Colors.Dark]]] = None,
    ):
        self.name = name
        self.label = label
        self.unread_count = unread_count
        self.total_count = total_count
        self.last_email_received_at = last_email_received_at
        self._colors = colors or Colors.Light
        self.accent_color = color or self._colors.ACCENT
        self.accent_color_secondary = color_secondary
        self._on_click = on_click
        self._on_refresh = on_refresh

        c = self._colors  # Shorthand

        self.refresh_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            icon_size=16,
            icon_color=c.TEXT_TERTIARY,
            tooltip="Refresh",
            visible=False,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
                padding=Spacing.XXS,
            ),
            on_click=self._handle_refresh,
        )

        super().__init__(
            content=self._build_content(),
            padding=ft.padding.symmetric(
                horizontal=Spacing.MD,
                vertical=Spacing.SM,
            ),
            border=ft.border.only(
                bottom=ft.BorderSide(1, c.BORDER_SUBTLE)
            ),
            on_hover=self._on_hover,
            on_click=self._handle_click,
            ink=True,
        )

    def _build_content(self) -> ft.Control:
        """Build list item content."""
        c = self._colors  # Shorthand

        # Unread badge
        unread_badge = ft.Container(
            content=ft.Text(
                f"{self.unread_count} unread",
                size=Typography.CAPTION_SIZE,
                color=c.BG_PRIMARY if self.unread_count > 0 else c.TEXT_TERTIARY,
                weight=ft.FontWeight.W_500,
            ),
            bgcolor=c.ACCENT if self.unread_count > 0 else None,
            border_radius=BorderRadius.SM,
            padding=ft.padding.symmetric(
                horizontal=Spacing.XS,
                vertical=Spacing.XXS,
            ),
            visible=True,
        )

        return ft.Row(
            [
                # Color dot (with gradient support)
                create_gradient_dot(
                    self.accent_color,
                    self.accent_color_secondary,
                    size=8,
                ),
                ft.Container(width=Spacing.SM),
                # Name and label
                ft.Column(
                    [
                        ft.Text(
                            self.name,
                            size=Typography.BODY_SIZE,
                            weight=ft.FontWeight.W_500,
                            color=c.TEXT_PRIMARY,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Text(
                            self.label,
                            size=Typography.CAPTION_SIZE,
                            color=c.TEXT_TERTIARY,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                    spacing=0,
                    expand=True,
                ),
                # Recent activity
                ft.Text(
                    format_relative_time(self.last_email_received_at),
                    size=Typography.CAPTION_SIZE,
                    color=c.TEXT_TERTIARY,
                    width=100,
                    text_align=ft.TextAlign.RIGHT,
                ),
                ft.Container(width=Spacing.MD),
                # Unread badge
                ft.Container(
                    content=unread_badge,
                    width=80,
                ),
                # Total count
                ft.Text(
                    str(self.total_count),
                    size=Typography.BODY_SMALL_SIZE,
                    color=c.TEXT_TERTIARY,
                    width=50,
                    text_align=ft.TextAlign.RIGHT,
                    font_family="monospace",
                ),
                ft.Container(width=Spacing.XS),
                # Refresh button (shown on hover)
                self.refresh_button,
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _on_hover(self, e: ft.HoverEvent) -> None:
        """Handle hover state."""
        c = self._colors
        if e.data == "true":
            self.bgcolor = c.BG_TERTIARY
            self.refresh_button.visible = True
        else:
            self.bgcolor = None
            self.refresh_button.visible = False
        self.refresh_button.update()
        self.update()

    def _handle_click(self, e: ft.ControlEvent) -> None:
        """Handle row click."""
        if self._on_click:
            self._on_click(e)

    def _handle_refresh(self, e: ft.ControlEvent) -> None:
        """Handle refresh button click."""
        e.control.data = "refresh"
        if self._on_refresh:
            self._on_refresh(e)
