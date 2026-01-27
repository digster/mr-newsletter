"""Dynamic color class generation from theme JSON.

Creates Colors-compatible classes at runtime from theme data,
with fallback to default design tokens for missing values.
"""

from typing import Optional, Type

from .design_tokens import Colors
from .theme_schema import ThemeColorSet, ThemeSchema


def _get_color_with_fallback(
    theme_colors: Optional[ThemeColorSet],
    attr_name: str,
    default_class: Type,
) -> str:
    """Get a color value with fallback to default.

    Args:
        theme_colors: Theme color set (may be None).
        attr_name: Attribute name in snake_case (e.g., 'bg_primary').
        default_class: Default Colors class (Colors.Light or Colors.Dark).

    Returns:
        Color value (hex string).
    """
    if theme_colors is not None:
        # Try to get value from theme (snake_case in schema)
        value = getattr(theme_colors, attr_name, None)
        if value is not None:
            return value

    # Fallback to default (UPPER_SNAKE_CASE in Colors class)
    default_attr = attr_name.upper()
    return getattr(default_class, default_attr)


def create_light_colors_from_theme(theme: ThemeSchema) -> Type:
    """Create a Light colors class from theme schema.

    Args:
        theme: Validated theme schema.

    Returns:
        A class with color attributes matching Colors.Light interface.
    """
    theme_colors = theme.colors.light if theme.colors else None
    default = Colors.Light

    class ThemeLightColors:
        """Dynamically generated light mode colors."""

        # Background layers
        BG_PRIMARY = _get_color_with_fallback(theme_colors, "bg_primary", default)
        BG_SECONDARY = _get_color_with_fallback(theme_colors, "bg_secondary", default)
        BG_TERTIARY = _get_color_with_fallback(theme_colors, "bg_tertiary", default)
        BG_ELEVATED = _get_color_with_fallback(theme_colors, "bg_elevated", default)

        # Text hierarchy
        TEXT_PRIMARY = _get_color_with_fallback(theme_colors, "text_primary", default)
        TEXT_SECONDARY = _get_color_with_fallback(theme_colors, "text_secondary", default)
        TEXT_TERTIARY = _get_color_with_fallback(theme_colors, "text_tertiary", default)
        TEXT_DISABLED = _get_color_with_fallback(theme_colors, "text_disabled", default)

        # Borders
        BORDER_DEFAULT = _get_color_with_fallback(theme_colors, "border_default", default)
        BORDER_SUBTLE = _get_color_with_fallback(theme_colors, "border_subtle", default)
        BORDER_STRONG = _get_color_with_fallback(theme_colors, "border_strong", default)

        # Interactive states
        HOVER = _get_color_with_fallback(theme_colors, "hover", default)
        ACTIVE = _get_color_with_fallback(theme_colors, "active", default)
        FOCUS_RING = _get_color_with_fallback(theme_colors, "focus_ring", default)

        # Accent
        ACCENT = _get_color_with_fallback(theme_colors, "accent", default)
        ACCENT_HOVER = _get_color_with_fallback(theme_colors, "accent_hover", default)
        ACCENT_MUTED = _get_color_with_fallback(theme_colors, "accent_muted", default)

        # Semantic colors
        SUCCESS = _get_color_with_fallback(theme_colors, "success", default)
        SUCCESS_MUTED = _get_color_with_fallback(theme_colors, "success_muted", default)
        WARNING = _get_color_with_fallback(theme_colors, "warning", default)
        WARNING_MUTED = _get_color_with_fallback(theme_colors, "warning_muted", default)
        ERROR = _get_color_with_fallback(theme_colors, "error", default)
        ERROR_MUTED = _get_color_with_fallback(theme_colors, "error_muted", default)

        # Special
        UNREAD_DOT = _get_color_with_fallback(theme_colors, "unread_dot", default)
        STAR_ACTIVE = _get_color_with_fallback(theme_colors, "star_active", default)
        STAR_INACTIVE = _get_color_with_fallback(theme_colors, "star_inactive", default)

    return ThemeLightColors


def create_dark_colors_from_theme(theme: ThemeSchema) -> Type:
    """Create a Dark colors class from theme schema.

    Args:
        theme: Validated theme schema.

    Returns:
        A class with color attributes matching Colors.Dark interface.
    """
    theme_colors = theme.colors.dark if theme.colors else None
    default = Colors.Dark

    class ThemeDarkColors:
        """Dynamically generated dark mode colors."""

        # Background layers
        BG_PRIMARY = _get_color_with_fallback(theme_colors, "bg_primary", default)
        BG_SECONDARY = _get_color_with_fallback(theme_colors, "bg_secondary", default)
        BG_TERTIARY = _get_color_with_fallback(theme_colors, "bg_tertiary", default)
        BG_ELEVATED = _get_color_with_fallback(theme_colors, "bg_elevated", default)

        # Text hierarchy
        TEXT_PRIMARY = _get_color_with_fallback(theme_colors, "text_primary", default)
        TEXT_SECONDARY = _get_color_with_fallback(theme_colors, "text_secondary", default)
        TEXT_TERTIARY = _get_color_with_fallback(theme_colors, "text_tertiary", default)
        TEXT_DISABLED = _get_color_with_fallback(theme_colors, "text_disabled", default)

        # Borders
        BORDER_DEFAULT = _get_color_with_fallback(theme_colors, "border_default", default)
        BORDER_SUBTLE = _get_color_with_fallback(theme_colors, "border_subtle", default)
        BORDER_STRONG = _get_color_with_fallback(theme_colors, "border_strong", default)

        # Interactive states
        HOVER = _get_color_with_fallback(theme_colors, "hover", default)
        ACTIVE = _get_color_with_fallback(theme_colors, "active", default)
        FOCUS_RING = _get_color_with_fallback(theme_colors, "focus_ring", default)

        # Accent
        ACCENT = _get_color_with_fallback(theme_colors, "accent", default)
        ACCENT_HOVER = _get_color_with_fallback(theme_colors, "accent_hover", default)
        ACCENT_MUTED = _get_color_with_fallback(theme_colors, "accent_muted", default)

        # Semantic colors
        SUCCESS = _get_color_with_fallback(theme_colors, "success", default)
        SUCCESS_MUTED = _get_color_with_fallback(theme_colors, "success_muted", default)
        WARNING = _get_color_with_fallback(theme_colors, "warning", default)
        WARNING_MUTED = _get_color_with_fallback(theme_colors, "warning_muted", default)
        ERROR = _get_color_with_fallback(theme_colors, "error", default)
        ERROR_MUTED = _get_color_with_fallback(theme_colors, "error_muted", default)

        # Special
        UNREAD_DOT = _get_color_with_fallback(theme_colors, "unread_dot", default)
        STAR_ACTIVE = _get_color_with_fallback(theme_colors, "star_active", default)
        STAR_INACTIVE = _get_color_with_fallback(theme_colors, "star_inactive", default)

    return ThemeDarkColors


def create_colors_from_theme(theme: ThemeSchema) -> tuple[Type, Type]:
    """Create both Light and Dark color classes from a theme.

    Args:
        theme: Validated theme schema.

    Returns:
        Tuple of (LightColors, DarkColors) classes.
    """
    return (
        create_light_colors_from_theme(theme),
        create_dark_colors_from_theme(theme),
    )
