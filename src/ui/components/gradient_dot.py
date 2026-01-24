"""Gradient dot component for newsletter color display."""

from typing import Optional

import flet as ft

from src.ui.themes import BorderRadius


def create_gradient_dot(
    color: str,
    color_secondary: Optional[str] = None,
    size: int = 8,
) -> ft.Container:
    """Create a dot with solid color or gradient.

    Args:
        color: Primary hex color.
        color_secondary: Optional secondary hex color for gradient.
        size: Dot diameter in pixels.

    Returns:
        Container with solid or gradient background.
    """
    if color_secondary:
        # Gradient background (top-left to bottom-right diagonal)
        return ft.Container(
            width=size,
            height=size,
            border_radius=BorderRadius.FULL,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(-1, -1),  # top-left
                end=ft.Alignment(1, 1),      # bottom-right
                colors=[color, color_secondary],
            ),
        )
    else:
        # Solid color
        return ft.Container(
            width=size,
            height=size,
            border_radius=BorderRadius.FULL,
            bgcolor=color,
        )
