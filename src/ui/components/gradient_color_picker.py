"""Gradient color picker component with HSV color picker popup."""

import colorsys
import re
import time
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


def _get_contrast_color(hex_color: str) -> str:
    """Get contrasting text color (black or white) based on background luminance."""
    if not hex_color or not _is_valid_hex(hex_color):
        return "#000000"
    hex_val = hex_color.lstrip("#")
    r, g, b = int(hex_val[0:2], 16), int(hex_val[2:4], 16), int(hex_val[4:6], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#000000" if luminance > 0.5 else "#FFFFFF"


def _is_valid_hex(value: str) -> bool:
    """Check if a string is a valid hex color."""
    if not value:
        return False
    pattern = r"^#[0-9A-Fa-f]{6}$"
    return bool(re.match(pattern, value))


def _hsv_to_hex(h: float, s: float, v: float) -> str:
    """Convert HSV to hex color.

    Args:
        h: Hue (0-360)
        s: Saturation (0-1)
        v: Value (0-1)

    Returns:
        Hex color string like "#FF0000"
    """
    r, g, b = colorsys.hsv_to_rgb(h / 360, s, v)
    return f"#{int(r * 255):02X}{int(g * 255):02X}{int(b * 255):02X}"


def _hex_to_hsv(hex_color: str) -> Tuple[float, float, float]:
    """Convert hex color to HSV.

    Args:
        hex_color: Hex color string like "#FF0000"

    Returns:
        Tuple of (hue: 0-360, saturation: 0-1, value: 0-1)
    """
    if not _is_valid_hex(hex_color):
        return (0.0, 1.0, 1.0)  # Default to red
    hex_val = hex_color.lstrip("#")
    r = int(hex_val[0:2], 16) / 255
    g = int(hex_val[2:4], 16) / 255
    b = int(hex_val[4:6], 16) / 255
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    return (h * 360, s, v)


class HSVColorPicker(ft.Column):
    """HSV color picker using sliders for Hue, Saturation, and Value.

    This implementation uses native Flet Sliders instead of a custom SV square
    to avoid the Stack rendering bug in Flet/Flutter.
    """

    SLIDER_WIDTH = 200  # Width of sliders

    def __init__(
        self,
        initial_color: str,
        on_change: Optional[Callable[[str], None]] = None,
    ):
        """Initialize HSV color picker.

        Args:
            initial_color: Initial hex color.
            on_change: Callback when color changes.
        """
        self._on_change = on_change
        self._hue, self._sat, self._val = _hex_to_hsv(initial_color)

        # Throttle state for slider updates (limits to ~20fps during dragging)
        self._last_update_time: float = 0
        self._throttle_ms: int = 50

        # Build components
        self._color_indicator = self._build_color_indicator()
        self._hue_slider = self._build_hue_slider()
        self._sat_slider = self._build_sat_slider()
        self._val_slider = self._build_val_slider()
        self._hex_display = self._build_hex_display()

        super().__init__(
            controls=[
                # Color indicator at top
                self._color_indicator,
                ft.Container(height=Spacing.MD),
                # Hue slider with rainbow gradient
                self._build_labeled_slider("Hue", self._hue_slider),
                ft.Container(height=Spacing.XS),
                # Saturation slider
                self._build_labeled_slider("Saturation", self._sat_slider),
                ft.Container(height=Spacing.XS),
                # Value slider
                self._build_labeled_slider("Brightness", self._val_slider),
                ft.Container(height=Spacing.SM),
                # Hex display
                self._hex_display,
            ],
            spacing=0,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _build_color_indicator(self) -> ft.Container:
        """Build the color preview indicator."""
        current_color = _hsv_to_hex(self._hue, self._sat, self._val)
        return ft.Container(
            width=self.SLIDER_WIDTH,
            height=40,
            bgcolor=current_color,
            border_radius=BorderRadius.SM,
            border=ft.border.all(1, Colors.Light.BORDER_DEFAULT),
        )

    def _build_hue_slider(self) -> ft.Slider:
        """Build the hue slider (0-360)."""
        return ft.Slider(
            min=0,
            max=360,
            value=self._hue,
            active_color=_hsv_to_hex(self._hue, 1, 1),
            thumb_color=_hsv_to_hex(self._hue, 1, 1),
            inactive_color=Colors.Light.BORDER_DEFAULT,
            width=self.SLIDER_WIDTH,
            on_change=self._on_hue_change,
            on_change_end=self._on_hue_change_end,
        )

    def _build_sat_slider(self) -> ft.Slider:
        """Build the saturation slider (0-100)."""
        return ft.Slider(
            min=0,
            max=100,
            value=self._sat * 100,
            active_color=_hsv_to_hex(self._hue, self._sat, 1),
            thumb_color=_hsv_to_hex(self._hue, self._sat, 1),
            inactive_color=Colors.Light.BORDER_DEFAULT,
            width=self.SLIDER_WIDTH,
            on_change=self._on_sat_change,
            on_change_end=self._on_sat_change_end,
        )

    def _build_val_slider(self) -> ft.Slider:
        """Build the value/brightness slider (0-100)."""
        return ft.Slider(
            min=0,
            max=100,
            value=self._val * 100,
            active_color=_hsv_to_hex(self._hue, self._sat, self._val),
            thumb_color=_hsv_to_hex(self._hue, self._sat, self._val),
            inactive_color=Colors.Light.BORDER_DEFAULT,
            width=self.SLIDER_WIDTH,
            on_change=self._on_val_change,
            on_change_end=self._on_val_change_end,
        )

    def _build_labeled_slider(self, label: str, slider: ft.Slider) -> ft.Column:
        """Build a slider with a label."""
        return ft.Column(
            controls=[
                ft.Text(
                    label,
                    size=Typography.CAPTION_SIZE,
                    color=Colors.Light.TEXT_TERTIARY,
                ),
                slider,
            ],
            spacing=2,
            horizontal_alignment=ft.CrossAxisAlignment.START,
        )

    def _build_hex_display(self) -> ft.Container:
        """Build hex color display."""
        current_color = _hsv_to_hex(self._hue, self._sat, self._val)
        text_color = _get_contrast_color(current_color)
        return ft.Container(
            content=ft.Text(
                current_color.upper(),
                size=Typography.BODY_SIZE,
                weight=ft.FontWeight.W_500,
                color=text_color,
            ),
            bgcolor=current_color,
            border_radius=BorderRadius.SM,
            border=ft.border.all(1, Colors.Light.BORDER_DEFAULT),
            padding=ft.padding.symmetric(horizontal=Spacing.MD, vertical=Spacing.XS),
            width=self.SLIDER_WIDTH,
            alignment=ft.alignment.Alignment(0, 0),
        )

    def _on_hue_change(self, e: ft.ControlEvent) -> None:
        """Handle hue slider change with throttling."""
        self._hue = e.control.value
        self._throttled_update()

    def _on_hue_change_end(self, e: ft.ControlEvent) -> None:
        """Handle hue slider change end - ensure final update."""
        self._hue = e.control.value
        self._force_update()

    def _on_sat_change(self, e: ft.ControlEvent) -> None:
        """Handle saturation slider change with throttling."""
        self._sat = e.control.value / 100
        self._throttled_update()

    def _on_sat_change_end(self, e: ft.ControlEvent) -> None:
        """Handle saturation slider change end - ensure final update."""
        self._sat = e.control.value / 100
        self._force_update()

    def _on_val_change(self, e: ft.ControlEvent) -> None:
        """Handle value/brightness slider change with throttling."""
        self._val = e.control.value / 100
        self._throttled_update()

    def _on_val_change_end(self, e: ft.ControlEvent) -> None:
        """Handle value/brightness slider change end - ensure final update."""
        self._val = e.control.value / 100
        self._force_update()

    def _throttled_update(self) -> None:
        """Update visuals with throttling to prevent UI lag."""
        current_time = time.time() * 1000
        if current_time - self._last_update_time >= self._throttle_ms:
            self._last_update_time = current_time
            self._update_slider_colors()
            self._update_display()
            self._notify_change()

    def _force_update(self) -> None:
        """Force immediate update without throttling (for final values)."""
        self._last_update_time = time.time() * 1000
        self._update_slider_colors()
        self._update_display()
        self._notify_change()

    def _update_slider_colors(self) -> None:
        """Update slider colors to reflect current HSV values."""
        # Update hue slider color
        hue_color = _hsv_to_hex(self._hue, 1, 1)
        self._hue_slider.active_color = hue_color
        self._hue_slider.thumb_color = hue_color

        # Update saturation slider color
        sat_color = _hsv_to_hex(self._hue, self._sat, 1)
        self._sat_slider.active_color = sat_color
        self._sat_slider.thumb_color = sat_color

        # Update value slider color
        val_color = _hsv_to_hex(self._hue, self._sat, self._val)
        self._val_slider.active_color = val_color
        self._val_slider.thumb_color = val_color

    def _update_display(self) -> None:
        """Update the color indicator and hex display."""
        current_color = _hsv_to_hex(self._hue, self._sat, self._val)
        text_color = _get_contrast_color(current_color)

        # Update color indicator
        self._color_indicator.bgcolor = current_color

        # Update hex display
        self._hex_display.bgcolor = current_color
        self._hex_display.content.value = current_color.upper()
        self._hex_display.content.color = text_color

        if self.page:
            self.update()

    def _notify_change(self) -> None:
        """Notify parent of color change."""
        if self._on_change:
            current_color = _hsv_to_hex(self._hue, self._sat, self._val)
            self._on_change(current_color)

    def get_color(self) -> str:
        """Get the current selected color."""
        return _hsv_to_hex(self._hue, self._sat, self._val)

    def set_color(self, hex_color: str) -> None:
        """Set the current color from hex."""
        self._hue, self._sat, self._val = _hex_to_hsv(hex_color)

        # Update slider values
        self._hue_slider.value = self._hue
        self._sat_slider.value = self._sat * 100
        self._val_slider.value = self._val * 100

        # Update colors and display
        self._update_slider_colors()
        self._update_display()


class ColorPickerPopup(ft.AlertDialog):
    """Popup dialog containing the HSV color picker."""

    def __init__(
        self,
        initial_color: str,
        on_select: Callable[[str], None],
        on_cancel: Optional[Callable[[], None]] = None,
    ):
        """Initialize color picker popup.

        Args:
            initial_color: Initial hex color.
            on_select: Callback when "Done" is clicked with selected color.
            on_cancel: Callback when "Cancel" is clicked.
        """
        self._initial_color = initial_color
        self._on_select = on_select
        self._on_cancel = on_cancel
        self._selected_color = initial_color

        self.hsv_picker = HSVColorPicker(
            initial_color=initial_color,
            on_change=self._on_color_change,
        )

        super().__init__(
            modal=True,
            title=ft.Text(
                "Choose Color",
                size=Typography.BODY_SIZE,
                weight=ft.FontWeight.W_500,
            ),
            content=ft.Container(
                content=self.hsv_picker,
                padding=ft.padding.only(top=Spacing.SM),
                height=330,  # Slider-based picker: indicator(40) + 3 sliders + hex display + spacing + button clearance
            ),
            actions=[
                ft.TextButton(
                    "Cancel",
                    on_click=self._handle_cancel,
                ),
                ft.ElevatedButton(
                    "Done",
                    on_click=self._handle_done,
                    bgcolor=Colors.Light.ACCENT,
                    color="#FFFFFF",
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

    def _on_color_change(self, color: str) -> None:
        """Handle color change from picker."""
        self._selected_color = color

    def _handle_done(self, e: ft.ControlEvent) -> None:
        """Handle Done button click."""
        self._on_select(self._selected_color)
        self.open = False
        if self.page:
            self.page.update()

    def _handle_cancel(self, e: ft.ControlEvent) -> None:
        """Handle Cancel button click."""
        if self._on_cancel:
            self._on_cancel()
        self.open = False
        if self.page:
            self.page.update()


class ColorField(ft.Container):
    """Clickable field that displays color and opens picker popup."""

    def __init__(
        self,
        label: str,
        color: str,
        on_change: Callable[[str], None],
        allow_clear: bool = False,
    ):
        """Initialize color field.

        Args:
            label: Field label.
            color: Current hex color.
            on_change: Callback when color changes.
            allow_clear: Whether to show clear button.
        """
        self._label = label
        self._color = color
        self._on_change = on_change
        self._allow_clear = allow_clear

        self._color_box = self._build_color_box()
        self._clear_btn = self._build_clear_btn() if allow_clear else None

        color_row_controls = [self._color_box]
        if self._clear_btn:
            color_row_controls.append(self._clear_btn)

        super().__init__(
            content=ft.Column(
                [
                    ft.Text(
                        label,
                        size=Typography.CAPTION_SIZE,
                        color=Colors.Light.TEXT_TERTIARY,
                    ),
                    ft.Container(height=Spacing.XXS),
                    ft.Row(
                        color_row_controls,
                        spacing=Spacing.XXS,
                    ),
                ],
                spacing=0,
            ),
        )

    def _build_color_box(self) -> ft.Container:
        """Build the clickable color display box."""
        has_color = self._color and _is_valid_hex(self._color)
        text_color = _get_contrast_color(self._color) if has_color else Colors.Light.TEXT_TERTIARY
        display_text = self._color.upper() if has_color else "None"

        return ft.Container(
            width=90,
            height=36,
            bgcolor=self._color if has_color else Colors.Light.BG_SECONDARY,
            border_radius=BorderRadius.SM,
            border=ft.border.all(1, Colors.Light.BORDER_DEFAULT),
            content=ft.Text(
                display_text,
                size=Typography.CAPTION_SIZE,
                weight=ft.FontWeight.W_500,
                color=text_color,
            ),
            alignment=ft.alignment.Alignment(0, 0),
            on_click=self._open_picker,
            tooltip="Click to choose color",
        )

    def _build_clear_btn(self) -> ft.Container:
        """Build clear button."""
        return ft.Container(
            content=ft.Icon(
                ft.Icons.CLOSE,
                size=14,
                color=Colors.Light.TEXT_TERTIARY,
            ),
            width=24,
            height=24,
            border_radius=BorderRadius.SM,
            bgcolor=Colors.Light.BG_SECONDARY,
            alignment=ft.alignment.Alignment(0, 0),
            on_click=self._clear_color,
            tooltip="Clear color",
            visible=self._color is not None and _is_valid_hex(self._color),
        )

    def _open_picker(self, e: ft.ControlEvent) -> None:
        """Open the color picker popup."""
        initial = self._color if _is_valid_hex(self._color) else "#FF6B6B"
        popup = ColorPickerPopup(
            initial_color=initial,
            on_select=self._on_color_selected,
        )
        self.page.show_dialog(popup)

    def _on_color_selected(self, color: str) -> None:
        """Handle color selection from popup."""
        self._color = color
        self._update_display()
        self._on_change(color)

    def _clear_color(self, e: ft.ControlEvent) -> None:
        """Clear the color."""
        self._color = None
        self._update_display()
        self._on_change(None)

    def _update_display(self) -> None:
        """Update the color box display."""
        has_color = self._color and _is_valid_hex(self._color)
        text_color = _get_contrast_color(self._color) if has_color else Colors.Light.TEXT_TERTIARY
        display_text = self._color.upper() if has_color else "None"

        self._color_box.bgcolor = self._color if has_color else Colors.Light.BG_SECONDARY
        self._color_box.content.value = display_text
        self._color_box.content.color = text_color

        if self._clear_btn:
            self._clear_btn.visible = has_color

        if self.page:
            self.update()

    def set_color(self, color: Optional[str]) -> None:
        """Set the color externally."""
        self._color = color
        self._update_display()

    def get_color(self) -> Optional[str]:
        """Get the current color."""
        return self._color


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

        # Color fields
        self.primary_field = ColorField(
            label="Primary",
            color=self._color,
            on_change=self._on_primary_change,
            allow_clear=False,
        )

        self.secondary_field = ColorField(
            label="Secondary (optional)",
            color=self._color_secondary,
            on_change=self._on_secondary_change,
            allow_clear=True,
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
                    # Color fields with preview
                    ft.Row(
                        [
                            self.primary_field,
                            ft.Container(width=Spacing.SM),
                            self.secondary_field,
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
                        vertical_alignment=ft.CrossAxisAlignment.START,
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
                ],
                tight=True,
            ),
            padding=ft.padding.only(top=Spacing.XS),
        )

    def _build_preview(self) -> ft.Container:
        """Build the preview dot."""
        if self._color_secondary and _is_valid_hex(self._color_secondary):
            return ft.Container(
                width=32,
                height=32,
                border_radius=BorderRadius.FULL,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(-1, -1),
                    end=ft.Alignment(1, 1),
                    colors=[self._color, self._color_secondary],
                ),
                border=ft.border.all(1, Colors.Light.BORDER_DEFAULT),
            )
        else:
            return ft.Container(
                width=32,
                height=32,
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
                    begin=ft.Alignment(-1, -1),
                    end=ft.Alignment(1, 1),
                    colors=[primary, secondary],
                ),
                border=ft.border.all(1, Colors.Light.BORDER_DEFAULT),
                on_click=lambda _, p=primary, s=secondary: self._apply_preset(p, s),
                tooltip=f"{primary} to {secondary}",
            )
            buttons.append(btn)
        return ft.Row(buttons, spacing=Spacing.XS, wrap=True)

    def _apply_preset(self, primary: str, secondary: str) -> None:
        """Apply a preset gradient."""
        self._color = primary
        self._color_secondary = secondary
        self.primary_field.set_color(primary)
        self.secondary_field.set_color(secondary)
        self._update_preview()
        self._notify_change()
        if self.page:
            self.update()

    def _on_primary_change(self, color: str) -> None:
        """Handle primary color change."""
        self._color = color
        self._update_preview()
        self._notify_change()
        if self.page:
            self.update()

    def _on_secondary_change(self, color: Optional[str]) -> None:
        """Handle secondary color change."""
        self._color_secondary = color
        self._update_preview()
        self._notify_change()
        if self.page:
            self.update()

    def _update_preview(self) -> None:
        """Update the preview dot."""
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
