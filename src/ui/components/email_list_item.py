"""Email list item component."""

import flet as ft
from datetime import datetime


class EmailListItem(ft.Container):
    """List item component for displaying an email."""

    def __init__(
        self,
        subject: str,
        sender: str,
        snippet: str,
        received_at: datetime,
        is_read: bool = False,
        is_starred: bool = False,
        on_click=None,
        on_star=None,
    ):
        self.subject = subject
        self.sender = sender
        self.snippet = snippet
        self.received_at = received_at
        self.is_read = is_read
        self.is_starred = is_starred

        date_str = received_at.strftime("%b %d")

        super().__init__(
            content=ft.Row(
                [
                    ft.IconButton(
                        icon=ft.Icons.STAR if is_starred else ft.Icons.STAR_BORDER,
                        icon_color=ft.Colors.AMBER if is_starred else None,
                        on_click=on_star,
                    ),
                    ft.Container(
                        width=8,
                        height=8,
                        border_radius=4,
                        bgcolor=ft.Colors.PRIMARY if not is_read else None,
                    ),
                    ft.Container(width=12),
                    ft.Column(
                        [
                            ft.Text(
                                subject,
                                size=14,
                                weight=ft.FontWeight.BOLD
                                if not is_read
                                else ft.FontWeight.NORMAL,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                sender,
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                            ),
                            ft.Text(
                                snippet,
                                size=12,
                                color=ft.Colors.ON_SURFACE_VARIANT,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                        spacing=2,
                        expand=True,
                    ),
                    ft.Text(
                        date_str,
                        size=12,
                        color=ft.Colors.ON_SURFACE_VARIANT,
                    ),
                ],
            ),
            padding=12,
            border_radius=8,
            ink=True,
            on_click=on_click,
            bgcolor=ft.Colors.SURFACE_CONTAINER if not is_read else None,
        )
