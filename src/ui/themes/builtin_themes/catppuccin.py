"""Catppuccin themes - Soothing pastel color palettes.

Palette source: https://catppuccin.com/palette

Catppuccin is a community-driven pastel theme with four flavors:
- Latte (light)
- Frappé (medium dark)
- Macchiato (darker)
- Mocha (darkest)

We implement Latte (light) and Mocha (dark) variants.

Latte (Light) base colors:
- Base: #EFF1F5
- Mantle: #E6E9EF
- Crust: #DCE0E8
- Surface0: #CCD0DA
- Surface1: #BCC0CC
- Surface2: #ACB0BE
- Text: #4C4F69
- Subtext1: #5C5F77
- Subtext0: #6C6F85

Mocha (Dark) base colors:
- Base: #1E1E2E
- Mantle: #181825
- Crust: #11111B
- Surface0: #313244
- Surface1: #45475A
- Surface2: #585B70
- Text: #CDD6F4
- Subtext1: #BAC2DE
- Subtext0: #A6ADC8

Accent colors (same names, different values per flavor):
- Rosewater, Flamingo, Pink, Mauve, Red, Maroon,
- Peach, Yellow, Green, Teal, Sky, Sapphire, Blue, Lavender
"""

CATPPUCCIN_LATTE_THEME = {
    "metadata": {
        "name": "Catppuccin Latte",
        "author": "Catppuccin",
        "version": "1.0.0",
        "description": "Soothing pastel light theme",
        "base": "light",
    },
    "colors": {
        "light": {
            # Latte base colors
            "bg_primary": "#EFF1F5",
            "bg_secondary": "#E6E9EF",
            "bg_tertiary": "#DCE0E8",
            "bg_elevated": "#FFFFFF",
            # Text colors
            "text_primary": "#4C4F69",
            "text_secondary": "#5C5F77",
            "text_tertiary": "#6C6F85",
            "text_disabled": "#9CA0B0",
            # Borders (Surface colors)
            "border_default": "#CCD0DA",
            "border_subtle": "#DCE0E8",
            "border_strong": "#BCC0CC",
            # Interactive
            "hover": "#E6E9EF",
            "active": "#DCE0E8",
            "focus_ring": "#8839EF",
            # Mauve accent
            "accent": "#8839EF",
            "accent_hover": "#7528D9",
            "accent_muted": "#EAE0FA",
            # Semantic
            "success": "#40A02B",
            "success_muted": "#DCF5D7",
            "warning": "#DF8E1D",
            "warning_muted": "#FBECD0",
            "error": "#D20F39",
            "error_muted": "#FBDBE2",
            # Special
            "unread_dot": "#04A5E5",
            "star_active": "#DF8E1D",
            "star_inactive": "#9CA0B0",
        },
        "dark": {
            # Mocha base colors for dark variant
            "bg_primary": "#1E1E2E",
            "bg_secondary": "#313244",
            "bg_tertiary": "#45475A",
            "bg_elevated": "#313244",
            # Text colors
            "text_primary": "#CDD6F4",
            "text_secondary": "#BAC2DE",
            "text_tertiary": "#A6ADC8",
            "text_disabled": "#585B70",
            # Borders
            "border_default": "#45475A",
            "border_subtle": "#313244",
            "border_strong": "#585B70",
            # Interactive
            "hover": "#313244",
            "active": "#45475A",
            "focus_ring": "#CBA6F7",
            # Mauve accent
            "accent": "#CBA6F7",
            "accent_hover": "#DDB9FF",
            "accent_muted": "#3E3559",
            # Semantic
            "success": "#A6E3A1",
            "success_muted": "#2D4A2B",
            "warning": "#F9E2AF",
            "warning_muted": "#4D4229",
            "error": "#F38BA8",
            "error_muted": "#4D2D36",
            # Special
            "unread_dot": "#89DCEB",
            "star_active": "#F9E2AF",
            "star_inactive": "#585B70",
        },
    },
}

CATPPUCCIN_MOCHA_THEME = {
    "metadata": {
        "name": "Catppuccin Mocha",
        "author": "Catppuccin",
        "version": "1.0.0",
        "description": "Soothing pastel dark theme",
        "base": "dark",
    },
    "colors": {
        "light": {
            # Latte for light variant
            "bg_primary": "#EFF1F5",
            "bg_secondary": "#E6E9EF",
            "bg_tertiary": "#DCE0E8",
            "bg_elevated": "#FFFFFF",
            "text_primary": "#4C4F69",
            "text_secondary": "#5C5F77",
            "text_tertiary": "#6C6F85",
            "text_disabled": "#9CA0B0",
            "border_default": "#CCD0DA",
            "border_subtle": "#DCE0E8",
            "border_strong": "#BCC0CC",
            "hover": "#E6E9EF",
            "active": "#DCE0E8",
            "focus_ring": "#8839EF",
            "accent": "#8839EF",
            "accent_hover": "#7528D9",
            "accent_muted": "#EAE0FA",
            "success": "#40A02B",
            "success_muted": "#DCF5D7",
            "warning": "#DF8E1D",
            "warning_muted": "#FBECD0",
            "error": "#D20F39",
            "error_muted": "#FBDBE2",
            "unread_dot": "#04A5E5",
            "star_active": "#DF8E1D",
            "star_inactive": "#9CA0B0",
        },
        "dark": {
            # Mocha dark
            "bg_primary": "#1E1E2E",
            "bg_secondary": "#313244",
            "bg_tertiary": "#45475A",
            "bg_elevated": "#313244",
            "text_primary": "#CDD6F4",
            "text_secondary": "#BAC2DE",
            "text_tertiary": "#A6ADC8",
            "text_disabled": "#585B70",
            "border_default": "#45475A",
            "border_subtle": "#313244",
            "border_strong": "#585B70",
            "hover": "#313244",
            "active": "#45475A",
            "focus_ring": "#CBA6F7",
            "accent": "#CBA6F7",
            "accent_hover": "#DDB9FF",
            "accent_muted": "#3E3559",
            "success": "#A6E3A1",
            "success_muted": "#2D4A2B",
            "warning": "#F9E2AF",
            "warning_muted": "#4D4229",
            "error": "#F38BA8",
            "error_muted": "#4D2D36",
            "unread_dot": "#89DCEB",
            "star_active": "#F9E2AF",
            "star_inactive": "#585B70",
        },
    },
}
