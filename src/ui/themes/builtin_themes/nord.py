"""Nord theme - Arctic, bluish-gray palette.

Palette source: https://www.nordtheme.com/docs/colors-and-palettes

Nord is an arctic, north-bluish color palette with four key sections:
- Polar Night: Dark backgrounds (#2E3440 - #4C566A)
- Snow Storm: Light text/backgrounds (#D8DEE9 - #ECEFF4)
- Frost: Blue accents (#8FBCBB - #5E81AC)
- Aurora: Semantic colors (red, orange, yellow, green, purple)
"""

NORD_THEME = {
    "metadata": {
        "name": "Nord",
        "author": "Arctic Ice Studio",
        "version": "1.0.0",
        "description": "Arctic, bluish-gray palette with muted colors",
        "base": "dark",
    },
    "colors": {
        "light": {
            # Snow Storm backgrounds
            "bg_primary": "#ECEFF4",
            "bg_secondary": "#E5E9F0",
            "bg_tertiary": "#D8DEE9",
            "bg_elevated": "#FFFFFF",
            # Polar Night text
            "text_primary": "#2E3440",
            "text_secondary": "#3B4252",
            "text_tertiary": "#4C566A",
            "text_disabled": "#7B88A1",
            # Borders
            "border_default": "#D8DEE9",
            "border_subtle": "#E5E9F0",
            "border_strong": "#C0C8D8",
            # Interactive
            "hover": "#E5E9F0",
            "active": "#D8DEE9",
            "focus_ring": "#5E81AC",
            # Frost accent
            "accent": "#5E81AC",
            "accent_hover": "#81A1C1",
            "accent_muted": "#D8DEE9",
            # Aurora semantic
            "success": "#A3BE8C",
            "success_muted": "#E5EBD8",
            "warning": "#EBCB8B",
            "warning_muted": "#F7EED8",
            "error": "#BF616A",
            "error_muted": "#F0D8DA",
            # Special
            "unread_dot": "#88C0D0",
            "star_active": "#EBCB8B",
            "star_inactive": "#C0C8D8",
        },
        "dark": {
            # Polar Night backgrounds
            "bg_primary": "#2E3440",
            "bg_secondary": "#3B4252",
            "bg_tertiary": "#434C5E",
            "bg_elevated": "#3B4252",
            # Snow Storm text
            "text_primary": "#ECEFF4",
            "text_secondary": "#E5E9F0",
            "text_tertiary": "#D8DEE9",
            "text_disabled": "#4C566A",
            # Borders
            "border_default": "#434C5E",
            "border_subtle": "#3B4252",
            "border_strong": "#4C566A",
            # Interactive
            "hover": "#3B4252",
            "active": "#434C5E",
            "focus_ring": "#88C0D0",
            # Frost accent
            "accent": "#88C0D0",
            "accent_hover": "#8FBCBB",
            "accent_muted": "#3B4252",
            # Aurora semantic
            "success": "#A3BE8C",
            "success_muted": "#3B4B3D",
            "warning": "#EBCB8B",
            "warning_muted": "#4D4232",
            "error": "#BF616A",
            "error_muted": "#4D3539",
            # Special
            "unread_dot": "#88C0D0",
            "star_active": "#EBCB8B",
            "star_inactive": "#4C566A",
        },
    },
}
