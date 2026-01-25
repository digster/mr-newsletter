"""Sort dropdown component for selecting newsletter sort order."""

from typing import Callable, Optional, Union

import flet as ft

from src.ui.themes import BorderRadius, Colors, Spacing, Typography


class SortDropdown(ft.Container):
    """Dropdown for selecting sort order."""

    SORT_OPTIONS = [
        ("recent", "Recent Activity"),
        ("unread", "Unread Count"),
        ("name_asc", "Name (A-Z)"),
        ("name_desc", "Name (Z-A)"),
    ]

    def __init__(
        self,
        current_sort: str = "recent",
        on_change: Optional[Callable[[str], None]] = None,
        colors: Optional[Union[type[Colors.Light], type[Colors.Dark]]] = None,
    ):
        self._current_sort = current_sort
        self._on_change_callback = on_change
        self._colors = colors or Colors.Light

        self.dropdown = ft.Dropdown(
            value=current_sort,
            options=[
                ft.dropdown.Option(key=key, text=label)
                for key, label in self.SORT_OPTIONS
            ],
            text_style=ft.TextStyle(
                size=Typography.BODY_SMALL_SIZE,
                color=self._colors.TEXT_SECONDARY,
            ),
            border=ft.InputBorder.NONE,
            content_padding=ft.Padding(
                left=Spacing.SM,
                right=Spacing.SM,
                top=Spacing.XS,
                bottom=Spacing.XS,
            ),
            width=160,
        )
        self.dropdown.on_change = self._handle_change

        super().__init__(
            content=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.SORT,
                        size=16,
                        color=self._colors.TEXT_TERTIARY,
                    ),
                    self.dropdown,
                ],
                spacing=Spacing.XXS,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.only(left=Spacing.SM),
            border_radius=BorderRadius.SM,
            bgcolor=self._colors.BG_TERTIARY,
        )

    def _handle_change(self, e: ft.ControlEvent) -> None:
        """Handle dropdown selection change."""
        self._current_sort = e.control.value
        if self._on_change_callback:
            self._on_change_callback(self._current_sort)

    @property
    def current_sort(self) -> str:
        """Get current sort value."""
        return self._current_sort

    @current_sort.setter
    def current_sort(self, sort_by: str) -> None:
        """Set current sort value."""
        self._current_sort = sort_by
        self.dropdown.value = sort_by
