"""View mode toggle component for switching between grid and list views."""

from typing import Callable, Optional, TYPE_CHECKING

import flet as ft

from src.ui.themes import BorderRadius, Colors, Spacing, get_colors

if TYPE_CHECKING:
    pass


class ViewModeToggle(ft.Container):
    """Toggle between grid and list view modes."""

    def __init__(
        self,
        current_mode: str = "grid",
        on_change: Optional[Callable[[str], None]] = None,
        colors: Optional[type] = None,
    ):
        self._current_mode = current_mode
        self._on_change_callback = on_change
        self._colors = colors or Colors.Light

        self.grid_button = self._build_button(
            icon=ft.Icons.GRID_VIEW,
            mode="grid",
            tooltip="Grid view",
        )
        self.list_button = self._build_button(
            icon=ft.Icons.VIEW_LIST,
            mode="list",
            tooltip="List view",
        )

        self._update_button_states()

        super().__init__(
            content=ft.Row(
                [self.grid_button, self.list_button],
                spacing=Spacing.XXS,
            ),
            padding=Spacing.XXS,
            border_radius=BorderRadius.SM,
            bgcolor=self._colors.BG_TERTIARY,
        )

    def _build_button(
        self,
        icon: str,
        mode: str,
        tooltip: str,
    ) -> ft.IconButton:
        """Build a toggle button."""
        return ft.IconButton(
            icon=icon,
            icon_size=18,
            tooltip=tooltip,
            data=mode,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
                padding=Spacing.XS,
            ),
            on_click=self._handle_click,
        )

    def _update_button_states(self) -> None:
        """Update visual states of buttons based on current mode."""
        self.grid_button.icon_color = (
            self._colors.ACCENT
            if self._current_mode == "grid"
            else self._colors.TEXT_TERTIARY
        )
        self.grid_button.bgcolor = (
            self._colors.BG_PRIMARY if self._current_mode == "grid" else None
        )

        self.list_button.icon_color = (
            self._colors.ACCENT
            if self._current_mode == "list"
            else self._colors.TEXT_TERTIARY
        )
        self.list_button.bgcolor = (
            self._colors.BG_PRIMARY if self._current_mode == "list" else None
        )

    def _handle_click(self, e: ft.ControlEvent) -> None:
        """Handle button click."""
        new_mode = e.control.data
        if new_mode != self._current_mode:
            self._current_mode = new_mode
            self._update_button_states()
            self.grid_button.update()
            self.list_button.update()

            if self._on_change_callback:
                self._on_change_callback(new_mode)

    @property
    def current_mode(self) -> str:
        """Get current view mode."""
        return self._current_mode

    @current_mode.setter
    def current_mode(self, mode: str) -> None:
        """Set current view mode."""
        self._current_mode = mode
        self._update_button_states()
