"""Gruvbox themes - Retro groove color scheme.

Palette source: https://github.com/morhetz/gruvbox

Gruvbox is a retro groove color scheme designed to be warm and earthy.
It comes in light and dark variants with vibrant, muted accent colors.

Dark mode backgrounds:
- bg0: #282828
- bg1: #3C3836
- bg2: #504945
- bg3: #665C54
- bg4: #7C6F64

Light mode backgrounds:
- bg0: #FBF1C7
- bg1: #EBDBB2
- bg2: #D5C4A1
- bg3: #BDAE93
- bg4: #A89984

Accent colors (bright variants for dark, muted for light):
- red: #FB4934 / #CC241D
- green: #B8BB26 / #98971A
- yellow: #FABD2F / #D79921
- blue: #83A598 / #458588
- purple: #D3869B / #B16286
- aqua: #8EC07C / #689D6A
- orange: #FE8019 / #D65D0E
"""

GRUVBOX_LIGHT_THEME = {
    "metadata": {
        "name": "Gruvbox Light",
        "author": "morhetz",
        "version": "1.0.0",
        "description": "Retro groove warm light theme",
        "base": "light",
    },
    "colors": {
        "light": {
            # Light backgrounds
            "bg_primary": "#FBF1C7",
            "bg_secondary": "#EBDBB2",
            "bg_tertiary": "#D5C4A1",
            "bg_elevated": "#FFFBEB",
            # Dark text
            "text_primary": "#282828",
            "text_secondary": "#3C3836",
            "text_tertiary": "#504945",
            "text_disabled": "#928374",
            # Borders
            "border_default": "#EBDBB2",
            "border_subtle": "#F2E5BC",
            "border_strong": "#D5C4A1",
            # Interactive
            "hover": "#EBDBB2",
            "active": "#D5C4A1",
            "focus_ring": "#458588",
            # Blue accent
            "accent": "#458588",
            "accent_hover": "#076678",
            "accent_muted": "#D5E3E5",
            # Semantic
            "success": "#98971A",
            "success_muted": "#E5E6C7",
            "warning": "#D79921",
            "warning_muted": "#F7EDCE",
            "error": "#CC241D",
            "error_muted": "#F5D5D3",
            # Special
            "unread_dot": "#689D6A",
            "star_active": "#D79921",
            "star_inactive": "#928374",
        },
        "dark": {
            # Dark backgrounds
            "bg_primary": "#282828",
            "bg_secondary": "#3C3836",
            "bg_tertiary": "#504945",
            "bg_elevated": "#3C3836",
            # Light text
            "text_primary": "#EBDBB2",
            "text_secondary": "#D5C4A1",
            "text_tertiary": "#BDAE93",
            "text_disabled": "#665C54",
            # Borders
            "border_default": "#3C3836",
            "border_subtle": "#282828",
            "border_strong": "#504945",
            # Interactive
            "hover": "#3C3836",
            "active": "#504945",
            "focus_ring": "#83A598",
            # Blue accent
            "accent": "#83A598",
            "accent_hover": "#8EC07C",
            "accent_muted": "#32403D",
            # Semantic
            "success": "#B8BB26",
            "success_muted": "#3D3D1A",
            "warning": "#FABD2F",
            "warning_muted": "#4D3D1A",
            "error": "#FB4934",
            "error_muted": "#4D2828",
            # Special
            "unread_dot": "#8EC07C",
            "star_active": "#FABD2F",
            "star_inactive": "#665C54",
        },
    },
}

GRUVBOX_DARK_THEME = {
    "metadata": {
        "name": "Gruvbox Dark",
        "author": "morhetz",
        "version": "1.0.0",
        "description": "Retro groove warm dark theme",
        "base": "dark",
    },
    "colors": {
        "light": {
            # Light backgrounds (same as Gruvbox Light)
            "bg_primary": "#FBF1C7",
            "bg_secondary": "#EBDBB2",
            "bg_tertiary": "#D5C4A1",
            "bg_elevated": "#FFFBEB",
            "text_primary": "#282828",
            "text_secondary": "#3C3836",
            "text_tertiary": "#504945",
            "text_disabled": "#928374",
            "border_default": "#EBDBB2",
            "border_subtle": "#F2E5BC",
            "border_strong": "#D5C4A1",
            "hover": "#EBDBB2",
            "active": "#D5C4A1",
            "focus_ring": "#458588",
            "accent": "#458588",
            "accent_hover": "#076678",
            "accent_muted": "#D5E3E5",
            "success": "#98971A",
            "success_muted": "#E5E6C7",
            "warning": "#D79921",
            "warning_muted": "#F7EDCE",
            "error": "#CC241D",
            "error_muted": "#F5D5D3",
            "unread_dot": "#689D6A",
            "star_active": "#D79921",
            "star_inactive": "#928374",
        },
        "dark": {
            # Dark backgrounds
            "bg_primary": "#282828",
            "bg_secondary": "#3C3836",
            "bg_tertiary": "#504945",
            "bg_elevated": "#3C3836",
            "text_primary": "#EBDBB2",
            "text_secondary": "#D5C4A1",
            "text_tertiary": "#BDAE93",
            "text_disabled": "#665C54",
            "border_default": "#3C3836",
            "border_subtle": "#282828",
            "border_strong": "#504945",
            "hover": "#3C3836",
            "active": "#504945",
            "focus_ring": "#83A598",
            "accent": "#83A598",
            "accent_hover": "#8EC07C",
            "accent_muted": "#32403D",
            "success": "#B8BB26",
            "success_muted": "#3D3D1A",
            "warning": "#FABD2F",
            "warning_muted": "#4D3D1A",
            "error": "#FB4934",
            "error_muted": "#4D2828",
            "unread_dot": "#8EC07C",
            "star_active": "#FABD2F",
            "star_inactive": "#665C54",
        },
    },
}
