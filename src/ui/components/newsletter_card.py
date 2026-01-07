"""Newsletter card component."""

import flet as ft


class NewsletterCard(ft.Card):
    """Card component for displaying a newsletter."""

    def __init__(
        self,
        name: str,
        label: str,
        unread_count: int,
        total_count: int,
        color: str = "#6750A4",
        on_click=None,
        on_refresh=None,
    ):
        self.name = name
        self.label = label
        self.unread_count = unread_count
        self.total_count = total_count
        self.color = color

        super().__init__(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Container(
                                    content=ft.Icon(
                                        ft.icons.EMAIL,
                                        color=ft.colors.WHITE,
                                    ),
                                    bgcolor=color,
                                    border_radius=8,
                                    padding=8,
                                ),
                                ft.Container(width=12),
                                ft.Column(
                                    [
                                        ft.Text(
                                            name,
                                            size=16,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            label,
                                            size=12,
                                            color=ft.colors.ON_SURFACE_VARIANT,
                                        ),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                            ],
                        ),
                        ft.Container(height=16),
                        ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(
                                            str(unread_count),
                                            size=24,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "Unread",
                                            size=12,
                                            color=ft.colors.ON_SURFACE_VARIANT,
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                                ft.Container(width=24),
                                ft.Column(
                                    [
                                        ft.Text(
                                            str(total_count),
                                            size=24,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            "Total",
                                            size=12,
                                            color=ft.colors.ON_SURFACE_VARIANT,
                                        ),
                                    ],
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                ),
                            ],
                        ),
                        ft.Container(height=16),
                        ft.Row(
                            [
                                ft.TextButton("View", on_click=on_click),
                                ft.IconButton(
                                    icon=ft.icons.REFRESH,
                                    on_click=on_refresh,
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ],
                ),
                padding=16,
            ),
        )
