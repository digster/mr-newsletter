"""Application theme configuration."""

import flet as ft


class AppTheme:
    """Application theme configuration."""

    # Primary colors
    PRIMARY = "#6750A4"  # Material 3 purple
    ON_PRIMARY = "#FFFFFF"
    PRIMARY_CONTAINER = "#EADDFF"
    ON_PRIMARY_CONTAINER = "#21005D"

    # Secondary colors
    SECONDARY = "#625B71"
    ON_SECONDARY = "#FFFFFF"
    SECONDARY_CONTAINER = "#E8DEF8"
    ON_SECONDARY_CONTAINER = "#1D192B"

    # Error colors
    ERROR = "#B3261E"
    ON_ERROR = "#FFFFFF"

    # Surface colors
    SURFACE = "#FFFBFE"
    ON_SURFACE = "#1C1B1F"
    SURFACE_VARIANT = "#E7E0EC"
    ON_SURFACE_VARIANT = "#49454F"

    @staticmethod
    def get_light_theme() -> ft.Theme:
        """Get light theme configuration."""
        return ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=AppTheme.PRIMARY,
                on_primary=AppTheme.ON_PRIMARY,
                primary_container=AppTheme.PRIMARY_CONTAINER,
                on_primary_container=AppTheme.ON_PRIMARY_CONTAINER,
                secondary=AppTheme.SECONDARY,
                on_secondary=AppTheme.ON_SECONDARY,
                secondary_container=AppTheme.SECONDARY_CONTAINER,
                on_secondary_container=AppTheme.ON_SECONDARY_CONTAINER,
                error=AppTheme.ERROR,
                on_error=AppTheme.ON_ERROR,
                surface=AppTheme.SURFACE,
                on_surface=AppTheme.ON_SURFACE,
            ),
        )

    @staticmethod
    def get_dark_theme() -> ft.Theme:
        """Get dark theme configuration."""
        return ft.Theme(
            color_scheme=ft.ColorScheme(
                primary="#D0BCFF",
                on_primary="#381E72",
                primary_container="#4F378B",
                on_primary_container="#EADDFF",
                secondary="#CCC2DC",
                on_secondary="#332D41",
                secondary_container="#4A4458",
                on_secondary_container="#E8DEF8",
                error="#F2B8B5",
                on_error="#601410",
                surface="#1C1B1F",
                on_surface="#E6E1E5",
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
