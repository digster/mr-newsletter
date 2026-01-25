"""Newsletter card component with sophisticated styling."""

from datetime import datetime
from typing import Callable, Optional, Union

import flet as ft

from src.ui.themes import BorderRadius, Colors, Shadows, Spacing, Typography
from src.ui.utils import format_relative_time


class NewsletterCard(ft.Container):
    """Card component for displaying a newsletter with premium depth."""

    def __init__(
        self,
        name: str,
        label: str,
        unread_count: int,
        total_count: int,
        last_email_received_at: Optional[datetime] = None,
        color: Optional[str] = None,
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
        self._on_click = on_click
        self._on_refresh = on_refresh

        c = self._colors  # Shorthand

        super().__init__(
            content=self._build_content(),
            padding=Spacing.SM,
            border_radius=BorderRadius.MD,
            border=ft.border.all(1, c.BORDER_DEFAULT),
            bgcolor=c.BG_PRIMARY,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=6,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
            on_hover=self._on_hover,
        )

    def _build_content(self) -> ft.Control:
        """Build card content."""
        c = self._colors  # Shorthand
        return ft.Column(
            [
                # Header row: Title on left, timestamp on right
                ft.Row(
                    [
                        ft.Text(
                            self.name,
                            size=Typography.H4_SIZE,
                            weight=ft.FontWeight.W_600,
                            color=c.TEXT_PRIMARY,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Container(expand=True),
                        ft.Icon(
                            ft.Icons.ACCESS_TIME,
                            size=14,
                            color=c.TEXT_TERTIARY,
                        ),
                        ft.Container(width=Spacing.XXS),
                        ft.Text(
                            format_relative_time(self.last_email_received_at),
                            size=Typography.CAPTION_SIZE,
                            color=c.TEXT_TERTIARY,
                        ),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                # Subtitle
                ft.Text(
                    self.label,
                    size=Typography.CAPTION_SIZE,
                    color=c.TEXT_TERTIARY,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Container(height=Spacing.MD),
                # Stats row - centered
                ft.Row(
                    [
                        self._build_stat(
                            str(self.unread_count),
                            "unread",
                            highlight=self.unread_count > 0,
                        ),
                        self._build_stat(str(self.total_count), "total"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=Spacing.XXL,
                ),
                ft.Container(height=Spacing.MD),
                # View emails button - full width with background
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(
                                "View emails",
                                size=Typography.BODY_SIZE,
                                weight=ft.FontWeight.W_500,
                                color=c.ACCENT,
                            ),
                            ft.Icon(
                                ft.Icons.ARROW_FORWARD,
                                size=18,
                                color=c.ACCENT,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=Spacing.XS,
                    ),
                    bgcolor=c.ACCENT_MUTED,
                    border_radius=BorderRadius.SM,
                    padding=ft.padding.symmetric(vertical=Spacing.SM),
                    on_click=self._on_click,
                ),
                ft.Container(height=Spacing.XS),
                # Refresh icon - right aligned
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.REFRESH,
                            icon_size=18,
                            icon_color=c.TEXT_TERTIARY,
                            tooltip="Refresh",
                            style=ft.ButtonStyle(
                                shape=ft.RoundedRectangleBorder(
                                    radius=BorderRadius.SM
                                ),
                            ),
                            on_click=self._on_refresh,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.END,
                ),
            ],
            spacing=0,
        )

    def _build_stat(
        self, value: str, label: str, highlight: bool = False
    ) -> ft.Control:
        """Build a stat display with large centered numbers."""
        c = self._colors
        return ft.Column(
            [
                ft.Text(
                    value,
                    size=Typography.H1_SIZE,
                    weight=ft.FontWeight.W_600,
                    color=c.ACCENT if highlight else c.TEXT_PRIMARY,
                ),
                ft.Text(
                    label,
                    size=Typography.CAPTION_SIZE,
                    color=c.TEXT_TERTIARY,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=Spacing.XXS,
        )

    def _on_hover(self, e: ft.HoverEvent) -> None:
        """Handle hover state with elevated shadow."""
        c = self._colors
        if e.data == "true":
            self.shadow = ft.BoxShadow(
                spread_radius=0,
                blur_radius=16,
                color=ft.Colors.with_opacity(0.12, ft.Colors.BLACK),
                offset=ft.Offset(0, 8),
            )
            self.border = ft.border.all(1, c.BORDER_STRONG)
        else:
            self.shadow = ft.BoxShadow(
                spread_radius=0,
                blur_radius=6,
                color=ft.Colors.with_opacity(0.08, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            )
            self.border = ft.border.all(1, c.BORDER_DEFAULT)
        self.update()
