"""Dracula theme - Dark theme with vibrant colors.

Palette source: https://draculatheme.com/contribute

Dracula is a dark theme with a distinctive purple accent and vibrant colors.
It's designed to be easy on the eyes while providing good contrast.

Key colors:
- Background: #282A36
- Current Line: #44475A
- Foreground: #F8F8F2
- Comment: #6272A4
- Cyan: #8BE9FD
- Green: #50FA7B
- Orange: #FFB86C
- Pink: #FF79C6
- Purple: #BD93F9
- Red: #FF5555
- Yellow: #F1FA8C
"""

DRACULA_THEME = {
    "metadata": {
        "name": "Dracula",
        "author": "Zeno Rocha",
        "version": "1.0.0",
        "description": "Dark theme with vibrant purple accent",
        "base": "dark",
    },
    "colors": {
        "light": {
            # Light variant inspired by Dracula palette
            "bg_primary": "#F8F8F2",
            "bg_secondary": "#F0F0E8",
            "bg_tertiary": "#E8E8E0",
            "bg_elevated": "#FFFFFF",
            "text_primary": "#282A36",
            "text_secondary": "#44475A",
            "text_tertiary": "#6272A4",
            "text_disabled": "#A0A4B8",
            "border_default": "#E8E8E0",
            "border_subtle": "#F0F0E8",
            "border_strong": "#D8D8D0",
            "hover": "#F0F0E8",
            "active": "#E8E8E0",
            "focus_ring": "#BD93F9",
            "accent": "#BD93F9",
            "accent_hover": "#A67DE8",
            "accent_muted": "#F3EBFF",
            "success": "#50FA7B",
            "success_muted": "#D8FFE2",
            "warning": "#FFB86C",
            "warning_muted": "#FFF0E0",
            "error": "#FF5555",
            "error_muted": "#FFE5E5",
            "unread_dot": "#8BE9FD",
            "star_active": "#F1FA8C",
            "star_inactive": "#A0A4B8",
        },
        "dark": {
            # Core Dracula dark
            "bg_primary": "#282A36",
            "bg_secondary": "#44475A",
            "bg_tertiary": "#4D5066",
            "bg_elevated": "#383A46",
            "text_primary": "#F8F8F2",
            "text_secondary": "#E0E0D8",
            "text_tertiary": "#BFBFB8",
            "text_disabled": "#6272A4",
            "border_default": "#44475A",
            "border_subtle": "#383A46",
            "border_strong": "#6272A4",
            "hover": "#383A46",
            "active": "#44475A",
            "focus_ring": "#BD93F9",
            "accent": "#BD93F9",
            "accent_hover": "#CCA4FF",
            "accent_muted": "#3D3654",
            "success": "#50FA7B",
            "success_muted": "#1A4D2E",
            "warning": "#FFB86C",
            "warning_muted": "#4D3D28",
            "error": "#FF5555",
            "error_muted": "#4D2828",
            "unread_dot": "#8BE9FD",
            "star_active": "#F1FA8C",
            "star_inactive": "#6272A4",
        },
    },
}
