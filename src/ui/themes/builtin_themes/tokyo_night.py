"""Tokyo Night theme - A clean, modern dark theme.

Palette source: https://github.com/enkia/tokyo-night-vscode-theme

Tokyo Night is a dark theme inspired by the lights of Tokyo at night.
It features a deep blue-gray background with soft, vibrant accent colors.

Base colors:
- Background: #1A1B26
- Background Dark: #16161E
- Background Highlight: #24283B
- Terminal Black: #414868
- Foreground: #C0CAF5
- Foreground Dark: #A9B1D6
- Comment: #565F89

Accent colors:
- Blue: #7AA2F7
- Cyan: #7DCFFF
- Green: #9ECE6A
- Magenta: #BB9AF7
- Orange: #FF9E64
- Red: #F7768E
- Yellow: #E0AF68
"""

TOKYO_NIGHT_THEME = {
    "metadata": {
        "name": "Tokyo Night",
        "author": "enkia",
        "version": "1.0.0",
        "description": "Clean, modern dark theme inspired by Tokyo",
        "base": "dark",
    },
    "colors": {
        "light": {
            # Tokyo Night Light/Day variant
            "bg_primary": "#D5D6DB",
            "bg_secondary": "#CBCCD1",
            "bg_tertiary": "#C1C2C7",
            "bg_elevated": "#E1E2E7",
            "text_primary": "#343B58",
            "text_secondary": "#4C505E",
            "text_tertiary": "#6C6F7E",
            "text_disabled": "#9699A3",
            "border_default": "#C1C2C7",
            "border_subtle": "#CBCCD1",
            "border_strong": "#B0B1B6",
            "hover": "#CBCCD1",
            "active": "#C1C2C7",
            "focus_ring": "#34548A",
            "accent": "#34548A",
            "accent_hover": "#2A4570",
            "accent_muted": "#D5DFF0",
            "success": "#485E30",
            "success_muted": "#DDE8D2",
            "warning": "#8F5E15",
            "warning_muted": "#F0E5D0",
            "error": "#8C4351",
            "error_muted": "#F0D8DB",
            "unread_dot": "#166775",
            "star_active": "#8F5E15",
            "star_inactive": "#9699A3",
        },
        "dark": {
            # Tokyo Night core dark
            "bg_primary": "#1A1B26",
            "bg_secondary": "#24283B",
            "bg_tertiary": "#2A2E42",
            "bg_elevated": "#24283B",
            "text_primary": "#C0CAF5",
            "text_secondary": "#A9B1D6",
            "text_tertiary": "#787C99",
            "text_disabled": "#565F89",
            "border_default": "#24283B",
            "border_subtle": "#1F2233",
            "border_strong": "#414868",
            "hover": "#24283B",
            "active": "#2A2E42",
            "focus_ring": "#7AA2F7",
            "accent": "#7AA2F7",
            "accent_hover": "#89B4FF",
            "accent_muted": "#2A3A5C",
            "success": "#9ECE6A",
            "success_muted": "#2D3D28",
            "warning": "#E0AF68",
            "warning_muted": "#4D3D28",
            "error": "#F7768E",
            "error_muted": "#4D2D36",
            "unread_dot": "#7DCFFF",
            "star_active": "#E0AF68",
            "star_inactive": "#565F89",
        },
    },
}
