"""Theme settings UI components.

Provides theme list, preview cards, and settings panel for the settings page.
"""

from typing import TYPE_CHECKING, Callable, Optional

import flet as ft

from src.services.theme_service import ThemeInfo, ThemeService, UNDELETABLE_THEME
from src.ui.themes import BorderRadius, Colors, Spacing, Typography, get_colors

if TYPE_CHECKING:
    pass


class ThemePreviewCard(ft.Container):
    """Small color preview card showing theme colors."""

    def __init__(
        self,
        preview_colors: tuple[str, str, str],
        size: int = 14,
    ):
        """Initialize theme preview card.

        Args:
            preview_colors: Tuple of (bg_primary, accent, text_primary).
            size: Size of each color swatch.
        """
        bg_primary, accent, text_primary = preview_colors

        super().__init__(
            content=ft.Row(
                [
                    ft.Container(
                        bgcolor=bg_primary,
                        width=size,
                        height=size,
                        border_radius=BorderRadius.SM,
                        border=ft.border.all(1, "#E5E5E5"),  # Neutral border for preview
                    ),
                    ft.Container(
                        bgcolor=accent,
                        width=size,
                        height=size,
                        border_radius=BorderRadius.SM,
                    ),
                    ft.Container(
                        bgcolor=text_primary,
                        width=size,
                        height=size,
                        border_radius=BorderRadius.SM,
                    ),
                ],
                spacing=4,
                tight=True,
            ),
        )


class ThemeListItem(ft.Container):
    """Theme list item showing theme info with selection and delete options."""

    def __init__(
        self,
        theme_info: ThemeInfo,
        is_active: bool,
        on_select: Optional[Callable[[ThemeInfo], None]] = None,
        on_delete: Optional[Callable[[ThemeInfo], None]] = None,
        colors: Optional[type] = None,
    ):
        """Initialize theme list item.

        Args:
            theme_info: Theme information to display.
            is_active: Whether this theme is currently active.
            on_select: Callback when theme is selected.
            on_delete: Callback when delete is clicked.
            colors: Colors class to use for styling.
        """
        self.theme_info = theme_info
        self.is_active = is_active
        self._on_select = on_select
        self._on_delete = on_delete
        self.colors = colors or Colors.Light

        c = self.colors

        # Build content
        name_row = ft.Row(
            [
                # Active indicator
                ft.Container(
                    width=8,
                    height=8,
                    border_radius=BorderRadius.FULL,
                    bgcolor=c.ACCENT if is_active else "transparent",
                ),
                ft.Container(width=Spacing.XS),
                # Theme name
                ft.Text(
                    theme_info.name,
                    size=Typography.BODY_SIZE,
                    weight=ft.FontWeight.W_500 if is_active else ft.FontWeight.W_400,
                    color=c.TEXT_PRIMARY,
                    expand=True,
                ),
                # Built-in badge
                ft.Container(
                    content=ft.Text(
                        "Built-in",
                        size=10,
                        color=c.TEXT_TERTIARY,
                    ),
                    visible=theme_info.is_builtin,
                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                    bgcolor=c.BG_TERTIARY,
                    border_radius=BorderRadius.SM,
                ),
                # Delete button (hidden only for undeletable default theme)
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_size=16,
                    icon_color=c.ERROR,
                    visible=theme_info.filename != UNDELETABLE_THEME,
                    style=ft.ButtonStyle(
                        padding=ft.padding.all(4),
                        shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
                    ),
                    on_click=self._handle_delete,
                    tooltip="Delete theme",
                ),
            ],
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        description_row = ft.Row(
            [
                ThemePreviewCard(theme_info.preview_colors),
                ft.Container(width=Spacing.SM),
                ft.Text(
                    theme_info.description or "No description",
                    size=Typography.CAPTION_SIZE,
                    color=c.TEXT_TERTIARY,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    expand=True,
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

        super().__init__(
            content=ft.Column(
                [
                    name_row,
                    ft.Container(height=Spacing.XXS),
                    description_row,
                ],
                spacing=0,
            ),
            padding=Spacing.SM,
            border_radius=BorderRadius.MD,
            border=ft.border.all(
                2 if is_active else 1,
                c.ACCENT if is_active else c.BORDER_DEFAULT,
            ),
            bgcolor=c.BG_PRIMARY,
            on_click=self._handle_click,
            ink=True,
        )

    def _handle_click(self, e: ft.ControlEvent) -> None:
        """Handle click on theme item."""
        if self._on_select:
            self._on_select(self.theme_info)

    def _handle_delete(self, e: ft.ControlEvent) -> None:
        """Handle delete button click."""
        e.control.page.run_task(self._async_handle_delete, e)

    async def _async_handle_delete(self, e: ft.ControlEvent) -> None:
        """Handle delete asynchronously to stop propagation."""
        if self._on_delete:
            self._on_delete(self.theme_info)


class ThemePreviewPanel(ft.AlertDialog):
    """Theme preview dialog with live preview mockup."""

    def __init__(
        self,
        theme_info: ThemeInfo,
        on_apply: Optional[Callable[[], None]] = None,
        on_cancel: Optional[Callable[[], None]] = None,
        colors: Optional[type] = None,
    ):
        """Initialize preview panel.

        Args:
            theme_info: Theme to preview.
            on_apply: Callback when apply is clicked.
            on_cancel: Callback when cancel is clicked.
            colors: Colors class to use for styling.
        """
        self.theme_info = theme_info
        self._on_apply = on_apply
        self._on_cancel = on_cancel
        c = colors or Colors.Light

        # Get preview colors
        bg_primary, accent, text_primary = theme_info.preview_colors

        # Build mockup preview
        preview = ft.Container(
            content=ft.Row(
                [
                    # Mini sidebar mockup
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Container(
                                    bgcolor=accent,
                                    width=40,
                                    height=6,
                                    border_radius=3,
                                ),
                                ft.Container(
                                    bgcolor=text_primary,
                                    width=30,
                                    height=6,
                                    border_radius=3,
                                    opacity=0.3,
                                ),
                                ft.Container(
                                    bgcolor=text_primary,
                                    width=35,
                                    height=6,
                                    border_radius=3,
                                    opacity=0.3,
                                ),
                            ],
                            spacing=8,
                        ),
                        bgcolor=bg_primary,
                        padding=Spacing.SM,
                        width=70,
                        height=120,
                        border_radius=BorderRadius.SM,
                        border=ft.border.all(1, c.BORDER_SUBTLE),
                    ),
                    ft.Container(width=Spacing.SM),
                    # Main content mockup
                    ft.Container(
                        content=ft.Column(
                            [
                                # Header
                                ft.Container(
                                    bgcolor=text_primary,
                                    width=80,
                                    height=8,
                                    border_radius=4,
                                ),
                                ft.Container(height=Spacing.SM),
                                # Cards
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Container(
                                                bgcolor=text_primary,
                                                width=100,
                                                height=6,
                                                border_radius=3,
                                            ),
                                            ft.Container(
                                                bgcolor=text_primary,
                                                width=60,
                                                height=4,
                                                border_radius=2,
                                                opacity=0.5,
                                            ),
                                        ],
                                        spacing=4,
                                    ),
                                    bgcolor=bg_primary,
                                    padding=Spacing.SM,
                                    border_radius=BorderRadius.SM,
                                    border=ft.border.all(1, c.BORDER_SUBTLE),
                                ),
                                ft.Container(height=Spacing.XS),
                                ft.Container(
                                    content=ft.Column(
                                        [
                                            ft.Container(
                                                bgcolor=text_primary,
                                                width=90,
                                                height=6,
                                                border_radius=3,
                                            ),
                                            ft.Container(
                                                bgcolor=text_primary,
                                                width=70,
                                                height=4,
                                                border_radius=2,
                                                opacity=0.5,
                                            ),
                                        ],
                                        spacing=4,
                                    ),
                                    bgcolor=bg_primary,
                                    padding=Spacing.SM,
                                    border_radius=BorderRadius.SM,
                                    border=ft.border.all(1, c.BORDER_SUBTLE),
                                ),
                            ],
                            spacing=0,
                        ),
                        expand=True,
                        height=120,
                    ),
                ],
                spacing=0,
            ),
            padding=Spacing.MD,
            border_radius=BorderRadius.MD,
            bgcolor=bg_primary,
            border=ft.border.all(1, c.BORDER_DEFAULT),
        )

        super().__init__(
            title=ft.Text(
                f"Preview: {theme_info.name}",
                size=Typography.H3_SIZE,
                weight=ft.FontWeight.W_600,
                color=c.TEXT_PRIMARY,
            ),
            content=ft.Container(
                content=ft.Column(
                    [
                        preview,
                        ft.Container(height=Spacing.SM),
                        ft.Text(
                            theme_info.description or "No description",
                            size=Typography.CAPTION_SIZE,
                            color=c.TEXT_TERTIARY,
                        ),
                    ],
                    tight=True,
                ),
                width=350,
                padding=ft.padding.only(top=Spacing.SM),
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    style=ft.ButtonStyle(
                        color=c.TEXT_SECONDARY,
                        padding=ft.padding.symmetric(
                            horizontal=Spacing.MD, vertical=Spacing.XS
                        ),
                    ),
                    on_click=lambda e: self._on_cancel() if self._on_cancel else None,
                ),
                ft.ElevatedButton(
                    "Apply Theme",
                    bgcolor=c.ACCENT,
                    color="#FFFFFF",
                    style=ft.ButtonStyle(
                        padding=ft.padding.symmetric(
                            horizontal=Spacing.MD, vertical=Spacing.XS
                        ),
                        shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
                    ),
                    on_click=lambda e: self._on_apply() if self._on_apply else None,
                ),
            ],
            actions_padding=ft.padding.all(Spacing.MD),
            content_padding=ft.padding.symmetric(horizontal=Spacing.LG),
            shape=ft.RoundedRectangleBorder(radius=BorderRadius.LG),
        )


class ThemeSettings(ft.Column):
    """Complete theme settings section for the settings page."""

    def __init__(
        self,
        flet_page: ft.Page,
        active_theme: str,
        on_theme_change: Optional[Callable[[str], None]] = None,
        on_import: Optional[Callable[[], None]] = None,
        on_export: Optional[Callable[[], None]] = None,
    ):
        """Initialize theme settings section.

        Args:
            flet_page: Flet page instance.
            active_theme: Currently active theme filename.
            on_theme_change: Callback when theme is changed.
            on_import: Callback when import button is clicked.
            on_export: Callback when export button is clicked.
        """
        self._flet_page = flet_page
        self.active_theme = active_theme
        self._on_theme_change = on_theme_change
        self._on_import = on_import
        self._on_export = on_export

        self.colors = get_colors(flet_page)
        self.theme_service = ThemeService()

        # Theme list container (will be populated)
        self.theme_list = ft.Column(spacing=Spacing.XS)

        # Wrap theme list in scrollable container with max height
        self._scrollable_theme_list = ft.Container(
            content=ft.Column(
                controls=[self.theme_list],
                scroll=ft.ScrollMode.AUTO,
            ),
            height=300,  # Max height before scrolling kicks in
        )

        # Build content
        super().__init__(
            controls=[
                self._scrollable_theme_list,
                ft.Container(height=Spacing.MD),
                ft.Row(
                    [
                        ft.OutlinedButton(
                            content=ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.FOLDER_OPEN,
                                        size=16,
                                        color=self.colors.TEXT_SECONDARY,
                                    ),
                                    ft.Container(width=Spacing.XS),
                                    ft.Text(
                                        "Import Theme",
                                        color=self.colors.TEXT_PRIMARY,
                                    ),
                                ],
                                tight=True,
                            ),
                            style=ft.ButtonStyle(
                                side=ft.BorderSide(1, self.colors.BORDER_DEFAULT),
                                shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
                            ),
                            on_click=self._handle_import,
                        ),
                        ft.Container(width=Spacing.SM),
                        ft.OutlinedButton(
                            content=ft.Row(
                                [
                                    ft.Icon(
                                        ft.Icons.SAVE_ALT,
                                        size=16,
                                        color=self.colors.TEXT_SECONDARY,
                                    ),
                                    ft.Container(width=Spacing.XS),
                                    ft.Text(
                                        "Export Current",
                                        color=self.colors.TEXT_PRIMARY,
                                    ),
                                ],
                                tight=True,
                            ),
                            style=ft.ButtonStyle(
                                side=ft.BorderSide(1, self.colors.BORDER_DEFAULT),
                                shape=ft.RoundedRectangleBorder(radius=BorderRadius.SM),
                            ),
                            on_click=self._handle_export,
                        ),
                    ],
                ),
            ],
            spacing=0,
        )

        # Load themes
        self._refresh_theme_list()

    def _refresh_theme_list(self) -> None:
        """Refresh the theme list."""
        themes = self.theme_service.list_themes()

        self.theme_list.controls.clear()

        for theme_info in themes:
            is_active = theme_info.filename == self.active_theme
            item = ThemeListItem(
                theme_info=theme_info,
                is_active=is_active,
                on_select=self._handle_select,
                on_delete=self._handle_delete,
                colors=self.colors,
            )
            self.theme_list.controls.append(item)

    def update_active_theme(self, theme_filename: str) -> None:
        """Update the active theme and refresh list.

        Args:
            theme_filename: New active theme filename.
        """
        self.active_theme = theme_filename
        self._refresh_theme_list()

        # Force update the entire control hierarchy
        # Flet needs explicit updates on nested containers
        try:
            if self.theme_list and self.theme_list.page:
                self.theme_list.update()
            if self._scrollable_theme_list and self._scrollable_theme_list.page:
                self._scrollable_theme_list.update()
            if self.page:
                self.update()
            if self._flet_page:
                self._flet_page.update()
        except Exception:
            pass  # Ignore update errors during initialization

    def _handle_select(self, theme_info: ThemeInfo) -> None:
        """Handle theme selection."""
        if theme_info.filename == self.active_theme:
            return  # Already active

        # Show preview dialog using Flet 0.80 API (show_dialog/pop_dialog)
        def apply_theme():
            self._flet_page.pop_dialog()
            if self._on_theme_change:
                self._on_theme_change(theme_info.filename)

        def cancel():
            self._flet_page.pop_dialog()

        dialog = ThemePreviewPanel(
            theme_info=theme_info,
            on_apply=apply_theme,
            on_cancel=cancel,
            colors=self.colors,
        )

        # Flet 0.80 API: use page.show_dialog() / page.pop_dialog()
        self._flet_page.show_dialog(dialog)

    def _handle_delete(self, theme_info: ThemeInfo) -> None:
        """Handle theme deletion."""
        from src.ui.components.dialogs import ConfirmDialog

        def confirm_delete(e: ft.ControlEvent):
            self._flet_page.pop_dialog()

            # Delete theme
            success, error = self.theme_service.delete_theme(theme_info.filename)
            if success:
                self._refresh_theme_list()
                self.update()
            else:
                # Show error using Flet 0.80 snackbar API
                snackbar = ft.SnackBar(
                    content=ft.Text(error or "Failed to delete theme"),
                    bgcolor=self.colors.ERROR,
                )
                self._flet_page.show_snack_bar(snackbar)

        def cancel(e: ft.ControlEvent):
            self._flet_page.pop_dialog()

        dialog = ConfirmDialog(
            title="Delete Theme",
            message=f"Are you sure you want to delete '{theme_info.name}'?",
            confirm_text="Delete",
            cancel_text="Cancel",
            is_destructive=True,
            on_confirm=confirm_delete,
            on_cancel=cancel,
            page=self._flet_page,
        )

        # Flet 0.80 API: use page.show_dialog() / page.pop_dialog()
        self._flet_page.show_dialog(dialog)

    def _handle_import(self, e: ft.ControlEvent) -> None:
        """Handle import button click."""
        if self._on_import:
            self._on_import()

    def _handle_export(self, e: ft.ControlEvent) -> None:
        """Handle export button click."""
        if self._on_export:
            self._on_export()

    def refresh(self) -> None:
        """Refresh the theme list from disk."""
        self._refresh_theme_list()
        self.update()
