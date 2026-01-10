"""Application theme configuration using design tokens."""

import flet as ft

from .design_tokens import Colors, Typography


class AppTheme:
    """Application theme with design token integration."""

    @staticmethod
    def get_light_theme() -> ft.Theme:
        """Get light theme configuration."""
        c = Colors.Light
        return ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=c.ACCENT,
                on_primary="#FFFFFF",
                primary_container=c.ACCENT_MUTED,
                on_primary_container=c.TEXT_PRIMARY,
                secondary=c.TEXT_SECONDARY,
                on_secondary="#FFFFFF",
                secondary_container=c.BG_SECONDARY,
                on_secondary_container=c.TEXT_PRIMARY,
                surface=c.BG_PRIMARY,
                on_surface=c.TEXT_PRIMARY,
                surface_container=c.BG_TERTIARY,
                on_surface_variant=c.TEXT_SECONDARY,
                outline=c.BORDER_DEFAULT,
                outline_variant=c.BORDER_SUBTLE,
                error=c.ERROR,
                on_error="#FFFFFF",
            ),
            text_theme=ft.TextTheme(
                headline_large=ft.TextStyle(
                    size=Typography.H1_SIZE,
                    weight=ft.FontWeight.W_600,
                ),
                headline_medium=ft.TextStyle(
                    size=Typography.H2_SIZE,
                    weight=ft.FontWeight.W_600,
                ),
                headline_small=ft.TextStyle(
                    size=Typography.H3_SIZE,
                    weight=ft.FontWeight.W_600,
                ),
                title_large=ft.TextStyle(
                    size=Typography.H4_SIZE,
                    weight=ft.FontWeight.W_500,
                ),
                title_medium=ft.TextStyle(
                    size=Typography.BODY_SIZE,
                    weight=ft.FontWeight.W_500,
                ),
                body_large=ft.TextStyle(
                    size=Typography.BODY_SIZE,
                    weight=ft.FontWeight.W_400,
                ),
                body_medium=ft.TextStyle(
                    size=Typography.BODY_SMALL_SIZE,
                    weight=ft.FontWeight.W_400,
                ),
                label_large=ft.TextStyle(
                    size=Typography.CAPTION_SIZE,
                    weight=ft.FontWeight.W_500,
                ),
                label_medium=ft.TextStyle(
                    size=Typography.CAPTION_SIZE,
                    weight=ft.FontWeight.W_400,
                ),
            ),
        )

    @staticmethod
    def get_dark_theme() -> ft.Theme:
        """Get dark theme configuration."""
        c = Colors.Dark
        return ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=c.ACCENT,
                on_primary=c.BG_PRIMARY,
                primary_container=c.ACCENT_MUTED,
                on_primary_container=c.TEXT_PRIMARY,
                secondary=c.TEXT_SECONDARY,
                on_secondary=c.BG_PRIMARY,
                secondary_container=c.BG_SECONDARY,
                on_secondary_container=c.TEXT_PRIMARY,
                surface=c.BG_PRIMARY,
                on_surface=c.TEXT_PRIMARY,
                surface_container=c.BG_TERTIARY,
                on_surface_variant=c.TEXT_SECONDARY,
                outline=c.BORDER_DEFAULT,
                outline_variant=c.BORDER_SUBTLE,
                error=c.ERROR,
                on_error=c.BG_PRIMARY,
            ),
            text_theme=ft.TextTheme(
                headline_large=ft.TextStyle(
                    size=Typography.H1_SIZE,
                    weight=ft.FontWeight.W_600,
                ),
                headline_medium=ft.TextStyle(
                    size=Typography.H2_SIZE,
                    weight=ft.FontWeight.W_600,
                ),
                headline_small=ft.TextStyle(
                    size=Typography.H3_SIZE,
                    weight=ft.FontWeight.W_600,
                ),
                title_large=ft.TextStyle(
                    size=Typography.H4_SIZE,
                    weight=ft.FontWeight.W_500,
                ),
                title_medium=ft.TextStyle(
                    size=Typography.BODY_SIZE,
                    weight=ft.FontWeight.W_500,
                ),
                body_large=ft.TextStyle(
                    size=Typography.BODY_SIZE,
                    weight=ft.FontWeight.W_400,
                ),
                body_medium=ft.TextStyle(
                    size=Typography.BODY_SMALL_SIZE,
                    weight=ft.FontWeight.W_400,
                ),
                label_large=ft.TextStyle(
                    size=Typography.CAPTION_SIZE,
                    weight=ft.FontWeight.W_500,
                ),
                label_medium=ft.TextStyle(
                    size=Typography.CAPTION_SIZE,
                    weight=ft.FontWeight.W_400,
                ),
            ),
        )


def get_theme(mode: str = "light") -> ft.Theme:
    """Get theme by mode.

    Args:
        mode: Theme mode ('light' or 'dark').

    Returns:
        Theme configuration.
    """
    if mode == "dark":
        return AppTheme.get_dark_theme()
    return AppTheme.get_light_theme()
