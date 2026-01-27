"""One Dark theme - Atom editor's iconic dark theme.

Palette source: Atom One Dark

One Dark is the default dark theme from the Atom text editor.
It features a dark gray background with vibrant syntax highlighting colors.

Base colors:
- Background: #282C34
- Gutter: #21252B
- Selection: #3E4451
- Line: #2C313A
- Comment: #5C6370

Syntax colors:
- Red: #E06C75
- Green: #98C379
- Yellow: #E5C07B
- Blue: #61AFEF
- Magenta: #C678DD
- Cyan: #56B6C2
- White: #ABB2BF
"""

ONE_DARK_THEME = {
    "metadata": {
        "name": "One Dark",
        "author": "Atom",
        "version": "1.0.0",
        "description": "Atom editor's iconic dark theme",
        "base": "dark",
    },
    "colors": {
        "light": {
            # One Light inspired variant
            "bg_primary": "#FAFAFA",
            "bg_secondary": "#F0F0F0",
            "bg_tertiary": "#E5E5E5",
            "bg_elevated": "#FFFFFF",
            "text_primary": "#383A42",
            "text_secondary": "#4F525D",
            "text_tertiary": "#696C77",
            "text_disabled": "#A0A1A7",
            "border_default": "#E5E5E5",
            "border_subtle": "#F0F0F0",
            "border_strong": "#D4D4D4",
            "hover": "#F0F0F0",
            "active": "#E5E5E5",
            "focus_ring": "#4078F2",
            "accent": "#4078F2",
            "accent_hover": "#2960DC",
            "accent_muted": "#E0E8FA",
            "success": "#50A14F",
            "success_muted": "#DCF0DC",
            "warning": "#C18401",
            "warning_muted": "#F5ECD0",
            "error": "#E45649",
            "error_muted": "#FAE0DE",
            "unread_dot": "#0184BC",
            "star_active": "#C18401",
            "star_inactive": "#A0A1A7",
        },
        "dark": {
            # One Dark core
            "bg_primary": "#282C34",
            "bg_secondary": "#21252B",
            "bg_tertiary": "#2C313A",
            "bg_elevated": "#2C313A",
            "text_primary": "#ABB2BF",
            "text_secondary": "#9DA5B4",
            "text_tertiary": "#7F848E",
            "text_disabled": "#5C6370",
            "border_default": "#3E4451",
            "border_subtle": "#2C313A",
            "border_strong": "#4B5263",
            "hover": "#2C313A",
            "active": "#3E4451",
            "focus_ring": "#61AFEF",
            "accent": "#61AFEF",
            "accent_hover": "#74BAFF",
            "accent_muted": "#2D3A4D",
            "success": "#98C379",
            "success_muted": "#2D3D2D",
            "warning": "#E5C07B",
            "warning_muted": "#4D4229",
            "error": "#E06C75",
            "error_muted": "#4D2D30",
            "unread_dot": "#56B6C2",
            "star_active": "#E5C07B",
            "star_inactive": "#5C6370",
        },
    },
}
