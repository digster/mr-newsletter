"""Search bar component for filtering newsletters."""

from typing import Callable, Optional

import flet as ft

from src.ui.themes import BorderRadius, Colors, Spacing, Typography


class SearchBar(ft.Container):
    """Search input with icon and clear button."""

    def __init__(
        self,
        placeholder: str = "Search newsletters...",
        on_change: Optional[Callable[[str], None]] = None,
        width: int = 280,
    ):
        self._on_change_callback = on_change
        self._width = width

        self.text_field = ft.TextField(
            hint_text=placeholder,
            hint_style=ft.TextStyle(
                size=Typography.BODY_SIZE,
                color=Colors.Light.TEXT_TERTIARY,
            ),
            text_style=ft.TextStyle(
                size=Typography.BODY_SIZE,
                color=Colors.Light.TEXT_PRIMARY,
            ),
            border=ft.InputBorder.NONE,
            content_padding=ft.padding.only(left=0, right=Spacing.XS),
            cursor_color=Colors.Light.ACCENT,
            expand=True,
            on_change=self._handle_change,
        )

        self.clear_button = ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_size=16,
            icon_color=Colors.Light.TEXT_TERTIARY,
            tooltip="Clear search",
            visible=False,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
                padding=Spacing.XXS,
            ),
            on_click=self._handle_clear,
        )

        super().__init__(
            content=ft.Row(
                [
                    ft.Icon(
                        ft.Icons.SEARCH,
                        size=18,
                        color=Colors.Light.TEXT_TERTIARY,
                    ),
                    ft.Container(width=Spacing.XS),
                    self.text_field,
                    self.clear_button,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
            ),
            width=width,
            height=40,
            padding=ft.Padding(
                left=Spacing.SM,
                right=Spacing.SM,
                top=0,
                bottom=0,
            ),
            border_radius=BorderRadius.SM,
            bgcolor=Colors.Light.BG_TERTIARY,
        )

    def _handle_change(self, e: ft.ControlEvent) -> None:
        """Handle text change with optional callback."""
        value = e.control.value or ""
        self.clear_button.visible = bool(value)
        self.clear_button.update()

        if self._on_change_callback:
            self._on_change_callback(value)

    def _handle_clear(self, e: ft.ControlEvent) -> None:
        """Clear the search field."""
        self.text_field.value = ""
        self.text_field.update()
        self.clear_button.visible = False
        self.clear_button.update()

        if self._on_change_callback:
            self._on_change_callback("")

    @property
    def value(self) -> str:
        """Get current search value."""
        return self.text_field.value or ""

    @value.setter
    def value(self, val: str) -> None:
        """Set search value."""
        self.text_field.value = val
        self.clear_button.visible = bool(val)
