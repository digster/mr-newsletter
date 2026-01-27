"""Liquid Glass theme - Apple-inspired translucent glass aesthetic.

Inspired by Apple's "Liquid Glass" design language from iOS 26 / macOS Tahoe.
Features translucent backgrounds with soft rim lighting using 8-digit hex colors
(#AARRGGBB format) for alpha transparency.

The glass effect is achieved through semi-transparent backgrounds that allow
underlying content to subtly show through, combined with white/light rim borders
that simulate light refraction on glass edges.
"""

LIQUID_GLASS_THEME = {
    "metadata": {
        "name": "Liquid Glass",
        "author": "Newsletter Reader",
        "version": "1.0.0",
        "description": "Apple-inspired translucent glass aesthetic with soft lighting",
        "base": "light",
    },
    "colors": {
        "light": {
            # Glass surfaces (semi-transparent whites)
            "bg_primary": "#B8FFFFFF",  # 72% white glass surface
            "bg_secondary": "#A6F8FAFC",  # 65% pale slate glass
            "bg_tertiary": "#CCF1F5F9",  # 80% container glass
            "bg_elevated": "#E0FFFFFF",  # 88% modal glass
            # Text (solid dark slate for readability)
            "text_primary": "#1E293B",  # Dark slate
            "text_secondary": "#475569",  # Medium slate
            "text_tertiary": "#94A3B8",  # Light slate
            "text_disabled": "#CBD5E1",  # Very light slate
            # White rim borders (simulate light refraction)
            "border_default": "#59FFFFFF",  # 35% white rim
            "border_subtle": "#33FFFFFF",  # 20% white rim
            "border_strong": "#80FFFFFF",  # 50% white rim
            # Interactive states
            "hover": "#C7F8FAFC",  # 78% hover state
            "active": "#E0F1F5F9",  # 88% pressed state
            "focus_ring": "#993B82F6",  # 60% blue focus
            # Accent (solid blue)
            "accent": "#3B82F6",  # Solid blue
            "accent_hover": "#2563EB",  # Darker blue
            "accent_muted": "#263B82F6",  # 15% translucent blue
            # Semantic colors
            "success": "#22C55E",  # Solid green
            "success_muted": "#2622C55E",  # 15% translucent green
            "warning": "#F59E0B",  # Solid amber
            "warning_muted": "#26F59E0B",  # 15% translucent amber
            "error": "#EF4444",  # Solid red
            "error_muted": "#26EF4444",  # 15% translucent red
            # Special
            "unread_dot": "#3B82F6",  # Blue indicator
            "star_active": "#F59E0B",  # Amber star
            "star_inactive": "#8094A3B8",  # 50% faded star
        },
        "dark": {
            # Glass surfaces (semi-transparent dark slates)
            "bg_primary": "#BF1E293B",  # 75% dark slate glass
            "bg_secondary": "#B3334155",  # 70% medium slate glass
            "bg_tertiary": "#BF475569",  # 75% lighter slate glass
            "bg_elevated": "#E0334155",  # 88% elevated glass
            # Text (light colors for dark mode)
            "text_primary": "#F8FAFC",  # Near white
            "text_secondary": "#E2E8F0",  # Light slate
            "text_tertiary": "#94A3B8",  # Medium slate
            "text_disabled": "#64748B",  # Dark slate
            # Blue-gray rim borders
            "border_default": "#3394A3B8",  # 20% blue-gray rim
            "border_subtle": "#2664748B",  # 15% subtle rim
            "border_strong": "#4DA8B9D4",  # 30% pronounced rim
            # Interactive states
            "hover": "#AD475569",  # 68% hover state
            "active": "#BF64748B",  # 75% pressed state
            "focus_ring": "#8060A5FA",  # 50% blue focus
            # Accent (lighter blue for dark mode)
            "accent": "#60A5FA",  # Light blue
            "accent_hover": "#3B82F6",  # Darker blue
            "accent_muted": "#3360A5FA",  # 20% translucent blue
            # Semantic colors
            "success": "#4ADE80",  # Light green
            "success_muted": "#334ADE80",  # 20% translucent green
            "warning": "#FBBF24",  # Light amber
            "warning_muted": "#33FBBF24",  # 20% translucent amber
            "error": "#F87171",  # Light red
            "error_muted": "#33F87171",  # 20% translucent red
            # Special
            "unread_dot": "#60A5FA",  # Blue indicator
            "star_active": "#FBBF24",  # Amber star
            "star_inactive": "#8064748B",  # 50% faded star
        },
    },
}
