"""Gradient color picker component for newsletter customization."""

import re
from typing import Callable, Optional, Tuple

import flet as ft

from src.ui.themes import BorderRadius, Colors, Spacing, Typography


# Preset gradient combinations for quick selection
PRESET_GRADIENTS = [
    ("#FF6B6B", "#4ECDC4"),  # Coral to Teal
    ("#667EEA", "#764BA2"),  # Purple gradient
    ("#F093FB", "#F5576C"),  # Pink gradient
    ("#4FACFE", "#00F2FE"),  # Blue to Cyan
    ("#43E97B", "#38F9D7"),  # Green gradient
    ("#FA709A", "#FEE140"),  # Pink to Yellow
    ("#A8EDEA", "#FED6E3"),  # Soft teal to pink
    ("#FF9A9E", "#FECFEF"),  # Soft coral to pink
]


def _is_valid_hex(value: str) -> bool:
    """Check if a string is a valid hex color."""
    if not value:
        return False
    pattern = r"^#[0-9A-Fa-f]{6}$"
    return bool(re.match(pattern, value))


class GradientColorPicker(ft.Container):
    """Color picker with gradient support and presets."""

    def __init__(
        self,
        initial_color: Optional[str] = None,
        initial_color_secondary: Optional[str] = None,
        on_change: Optional[Callable[[str, Optional[str]], None]] = None,
    ):
        """Initialize gradient color picker.

        Args:
            initial_color: Initial primary color.
            initial_color_secondary: Initial secondary color for gradient.
            on_change: Callback when colors change (color, color_secondary).
        """
        self._on_change = on_change
        self._color = initial_color or Colors.Light.ACCENT
        self._color_secondary = initial_color_secondary

        # Color input fields
        self.primary_input = ft.TextField(
            value=self._color,
            label="Primary Color",
            hint_text="#RRGGBB",
            width=120,
            border_radius=BorderRadius.SM,
            content_padding=ft.padding.symmetric(
                horizontal=Spacing.SM, vertical=Spacing.XS
            ),
            text_size=Typography.BODY_SMALL_SIZE,
            on_change=self._on_primary_change,
        )

        self.secondary_input = ft.TextField(
            value=self._color_secondary or "",
            label="Secondary Color",
            hint_text="#RRGGBB",
            width=120,
            border_radius=BorderRadius.SM,
            content_padding=ft.padding.symmetric(
                horizontal=Spacing.SM, vertical=Spacing.XS
            ),
            text_size=Typography.BODY_SMALL_SIZE,
            on_change=self._on_secondary_change,
        )

        # Preview dot
        self.preview = self._build_preview()

        # Build preset buttons
        self.presets_row = self._build_presets_row()

        super().__init__(
            content=ft.Column(
                [
                    # Section header
                    ft.Text(
                        "Color & Gradient",
                        size=Typography.CAPTION_SIZE,
                        weight=ft.FontWeight.W_500,
                        color=Colors.Light.TEXT_TERTIARY,
                    ),
                    ft.Container(height=Spacing.XS),
                    # Color inputs with preview
                    ft.Row(
                        [
                            self.primary_input,
                            ft.Container(width=Spacing.XS),
                            self.secondary_input,
                            ft.Container(width=Spacing.MD),
                            # Preview
                            ft.Column(
                                [
                                    ft.Text(
                                        "Preview",
                                        size=Typography.CAPTION_SIZE,
                                        color=Colors.Light.TEXT_TERTIARY,
                                    ),
                                    ft.Container(height=Spacing.XXS),
                                    self.preview,
                                ],
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=0,
                            ),
                        ],
                        vertical_alignment=ft.CrossAxisAlignment.END,
                    ),
                    ft.Container(height=Spacing.SM),
                    # Presets
                    ft.Text(
                        "Quick Presets",
                        size=Typography.CAPTION_SIZE,
                        color=Colors.Light.TEXT_TERTIARY,
                    ),
                    ft.Container(height=Spacing.XXS),
                    self.presets_row,
                    ft.Container(height=Spacing.XS),
                    # Clear secondary button
                    ft.TextButton(
                        content=ft.Row(
                            [
                                ft.Icon(
                                    ft.Icons.FORMAT_COLOR_RESET,
                                    size=14,
                                    color=Colors.Light.TEXT_TERTIARY,
                                ),
                                ft.Container(width=Spacing.XXS),
                                ft.Text(
                                    "Use solid color (clear secondary)",
                                    size=Typography.CAPTION_SIZE,
                                    color=Colors.Light.TEXT_TERTIARY,
                                ),
                            ],
                            spacing=0,
                        ),
                        style=ft.ButtonStyle(
                            padding=ft.padding.symmetric(
                                horizontal=Spacing.XS, vertical=Spacing.XXS
                            ),
                        ),
                        on_click=self._clear_secondary,
                    ),
                ],
                tight=True,
            ),
            padding=ft.padding.only(top=Spacing.XS),
        )

    def _build_preview(self) -> ft.Container:
        """Build the preview dot."""
        if self._color_secondary and _is_valid_hex(self._color_secondary):
            return ft.Container(
                width=24,
                height=24,
                border_radius=BorderRadius.FULL,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1),  # top-left
                    end=ft.Alignment(1, 1),      # bottom-right
                    colors=[self._color, self._color_secondary],
                ),
                border=ft.border.all(1, Colors.Light.BORDER_DEFAULT),
            )
        else:
            return ft.Container(
                width=24,
                height=24,
                border_radius=BorderRadius.FULL,
                bgcolor=self._color if _is_valid_hex(self._color) else Colors.Light.ACCENT,
                border=ft.border.all(1, Colors.Light.BORDER_DEFAULT),
            )

    def _build_presets_row(self) -> ft.Row:
        """Build row of preset gradient buttons."""
        buttons = []
        for primary, secondary in PRESET_GRADIENTS:
            btn = ft.Container(
                width=28,
                height=28,
                border_radius=BorderRadius.FULL,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1),  # top-left
                    end=ft.Alignment(1, 1),      # bottom-right
                    colors=[primary, secondary],
                ),
                border=ft.border.all(1, Colors.Light.BORDER_DEFAULT),
                on_click=lambda _, p=primary, s=secondary: self._apply_preset(p, s),
                tooltip=f"{primary} to {secondary}",
            )
            buttons.append(btn)
        return ft.Row(buttons, spacing=Spacing.XS)

    def _apply_preset(self, primary: str, secondary: str) -> None:
        """Apply a preset gradient."""
        self._color = primary
        self._color_secondary = secondary
        self.primary_input.value = primary
        self.secondary_input.value = secondary
        self._update_preview()
        self._notify_change()
        if self.page:
            self.update()

    def _on_primary_change(self, e: ft.ControlEvent) -> None:
        """Handle primary color input change."""
        value = e.control.value or ""
        # Add # if not present
        if value and not value.startswith("#"):
            value = f"#{value}"
            e.control.value = value

        if _is_valid_hex(value):
            self._color = value
            self._update_preview()
            self._notify_change()

    def _on_secondary_change(self, e: ft.ControlEvent) -> None:
        """Handle secondary color input change."""
        value = e.control.value or ""
        # Add # if not present
        if value and not value.startswith("#"):
            value = f"#{value}"
            e.control.value = value

        if not value:
            self._color_secondary = None
            self._update_preview()
            self._notify_change()
        elif _is_valid_hex(value):
            self._color_secondary = value
            self._update_preview()
            self._notify_change()

    def _clear_secondary(self, e: ft.ControlEvent) -> None:
        """Clear the secondary color."""
        self._color_secondary = None
        self.secondary_input.value = ""
        self._update_preview()
        self._notify_change()
        if self.page:
            self.update()

    def _update_preview(self) -> None:
        """Update the preview dot."""
        # Find the preview container in the layout and replace it
        # The preview is in Row -> Column (index 4) -> Container (index 2)
        new_preview = self._build_preview()
        self.preview.gradient = new_preview.gradient
        self.preview.bgcolor = new_preview.bgcolor

    def _notify_change(self) -> None:
        """Notify parent of color change."""
        if self._on_change:
            self._on_change(self._color, self._color_secondary)

    def get_colors(self) -> Tuple[str, Optional[str]]:
        """Get current color values.

        Returns:
            Tuple of (primary_color, secondary_color).
        """
        return self._color, self._color_secondary
