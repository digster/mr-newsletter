"""Solarized themes - Precision colors for machines and people.

Palette source: https://ethanschoonover.com/solarized/

Solarized is a sixteen color palette designed for use with terminal and GUI
applications. It has both light and dark modes that share the same accent colors.

Base colors:
- base03: #002B36 (dark bg)
- base02: #073642 (dark bg highlight)
- base01: #586E75 (dark content tone)
- base00: #657B83 (light content tone)
- base0: #839496 (dark content)
- base1: #93A1A1 (light content tone)
- base2: #EEE8D5 (light bg highlight)
- base3: #FDF6E3 (light bg)

Accent colors:
- yellow: #B58900
- orange: #CB4B16
- red: #DC322F
- magenta: #D33682
- violet: #6C71C4
- blue: #268BD2
- cyan: #2AA198
- green: #859900
"""

SOLARIZED_LIGHT_THEME = {
    "metadata": {
        "name": "Solarized Light",
        "author": "Ethan Schoonover",
        "version": "1.0.0",
        "description": "Warm cream background with blue/cyan accents",
        "base": "light",
    },
    "colors": {
        "light": {
            # Light mode - base3/base2 backgrounds
            "bg_primary": "#FDF6E3",
            "bg_secondary": "#EEE8D5",
            "bg_tertiary": "#E4DCC6",
            "bg_elevated": "#FFFFFF",
            # Dark bases for text
            "text_primary": "#073642",
            "text_secondary": "#586E75",
            "text_tertiary": "#657B83",
            "text_disabled": "#93A1A1",
            # Borders
            "border_default": "#EEE8D5",
            "border_subtle": "#F5EED9",
            "border_strong": "#D8D0B8",
            # Interactive
            "hover": "#EEE8D5",
            "active": "#E4DCC6",
            "focus_ring": "#268BD2",
            # Blue accent
            "accent": "#268BD2",
            "accent_hover": "#1A6699",
            "accent_muted": "#E8F4FC",
            # Semantic
            "success": "#859900",
            "success_muted": "#E8EDD0",
            "warning": "#B58900",
            "warning_muted": "#F5EDD0",
            "error": "#DC322F",
            "error_muted": "#FBEAE9",
            # Special
            "unread_dot": "#2AA198",
            "star_active": "#B58900",
            "star_inactive": "#93A1A1",
        },
        "dark": {
            # Dark mode - base03/base02 backgrounds
            "bg_primary": "#002B36",
            "bg_secondary": "#073642",
            "bg_tertiary": "#0D4652",
            "bg_elevated": "#073642",
            # Light bases for text
            "text_primary": "#FDF6E3",
            "text_secondary": "#EEE8D5",
            "text_tertiary": "#93A1A1",
            "text_disabled": "#586E75",
            # Borders
            "border_default": "#073642",
            "border_subtle": "#002B36",
            "border_strong": "#0D4652",
            # Interactive
            "hover": "#073642",
            "active": "#0D4652",
            "focus_ring": "#268BD2",
            # Blue accent
            "accent": "#268BD2",
            "accent_hover": "#3CA0E8",
            "accent_muted": "#0D3A47",
            # Semantic
            "success": "#859900",
            "success_muted": "#1A3300",
            "warning": "#B58900",
            "warning_muted": "#3D2E00",
            "error": "#DC322F",
            "error_muted": "#4A1110",
            # Special
            "unread_dot": "#2AA198",
            "star_active": "#B58900",
            "star_inactive": "#586E75",
        },
    },
}

SOLARIZED_DARK_THEME = {
    "metadata": {
        "name": "Solarized Dark",
        "author": "Ethan Schoonover",
        "version": "1.0.0",
        "description": "Dark blue-gray background with blue/cyan accents",
        "base": "dark",
    },
    "colors": {
        "light": {
            # Light variant (same as Solarized Light)
            "bg_primary": "#FDF6E3",
            "bg_secondary": "#EEE8D5",
            "bg_tertiary": "#E4DCC6",
            "bg_elevated": "#FFFFFF",
            "text_primary": "#073642",
            "text_secondary": "#586E75",
            "text_tertiary": "#657B83",
            "text_disabled": "#93A1A1",
            "border_default": "#EEE8D5",
            "border_subtle": "#F5EED9",
            "border_strong": "#D8D0B8",
            "hover": "#EEE8D5",
            "active": "#E4DCC6",
            "focus_ring": "#268BD2",
            "accent": "#268BD2",
            "accent_hover": "#1A6699",
            "accent_muted": "#E8F4FC",
            "success": "#859900",
            "success_muted": "#E8EDD0",
            "warning": "#B58900",
            "warning_muted": "#F5EDD0",
            "error": "#DC322F",
            "error_muted": "#FBEAE9",
            "unread_dot": "#2AA198",
            "star_active": "#B58900",
            "star_inactive": "#93A1A1",
        },
        "dark": {
            # Dark mode - base03/base02 backgrounds
            "bg_primary": "#002B36",
            "bg_secondary": "#073642",
            "bg_tertiary": "#0D4652",
            "bg_elevated": "#073642",
            "text_primary": "#FDF6E3",
            "text_secondary": "#EEE8D5",
            "text_tertiary": "#93A1A1",
            "text_disabled": "#586E75",
            "border_default": "#073642",
            "border_subtle": "#002B36",
            "border_strong": "#0D4652",
            "hover": "#073642",
            "active": "#0D4652",
            "focus_ring": "#268BD2",
            "accent": "#268BD2",
            "accent_hover": "#3CA0E8",
            "accent_muted": "#0D3A47",
            "success": "#859900",
            "success_muted": "#1A3300",
            "warning": "#B58900",
            "warning_muted": "#3D2E00",
            "error": "#DC322F",
            "error_muted": "#4A1110",
            "unread_dot": "#2AA198",
            "star_active": "#B58900",
            "star_inactive": "#586E75",
        },
    },
}
