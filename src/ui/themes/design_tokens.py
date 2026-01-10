"""Design token system for the newsletter reader app.

Sophistication & Trust design direction - cool slate tones with layered depth.
Inspired by Stripe and Mercury.
"""


class Spacing:
    """4px grid-based spacing tokens."""

    NONE = 0
    XXS = 4  # Micro spacing (icon gaps)
    XS = 8  # Element internal padding
    SM = 12  # Between related elements
    MD = 16  # Standard component padding
    LG = 24  # Section spacing
    XL = 32  # Large gaps
    XXL = 48  # Page-level spacing


class Typography:
    """Typography scale with semantic naming."""

    # Headlines
    H1_SIZE = 28
    H2_SIZE = 22
    H3_SIZE = 18
    H4_SIZE = 16

    # Body
    BODY_SIZE = 14
    BODY_SMALL_SIZE = 13
    CAPTION_SIZE = 12

    # Weights (map to FontWeight values)
    WEIGHT_BOLD = 600
    WEIGHT_MEDIUM = 500
    WEIGHT_REGULAR = 400

    # Letter spacing
    TRACKING_TIGHT = -0.02
    TRACKING_NORMAL = 0


class BorderRadius:
    """Consistent border radius system."""

    NONE = 0
    SM = 6  # Buttons, inputs, small elements
    MD = 8  # Cards, containers
    LG = 12  # Modals, large elements
    FULL = 999  # Pills, avatars


class Colors:
    """Sophistication & Trust palette - cool slate foundation with blue accent."""

    class Light:
        """Light mode colors."""

        # Background layers
        BG_PRIMARY = "#FFFFFF"  # Main background
        BG_SECONDARY = "#F8FAFC"  # Subtle alternate (slate-50)
        BG_TERTIARY = "#F1F5F9"  # Cards hover, containers (slate-100)
        BG_ELEVATED = "#FFFFFF"  # Modals, dropdowns

        # Text hierarchy
        TEXT_PRIMARY = "#0F172A"  # Headlines, primary (slate-900)
        TEXT_SECONDARY = "#475569"  # Body text (slate-600)
        TEXT_TERTIARY = "#94A3B8"  # Captions, hints (slate-400)
        TEXT_DISABLED = "#CBD5E1"  # Disabled text (slate-300)

        # Borders
        BORDER_DEFAULT = "#E2E8F0"  # Standard borders (slate-200)
        BORDER_SUBTLE = "#F1F5F9"  # Subtle dividers (slate-100)
        BORDER_STRONG = "#CBD5E1"  # Emphasized borders (slate-300)

        # Interactive states
        HOVER = "#F8FAFC"  # Hover background
        ACTIVE = "#F1F5F9"  # Active/pressed state
        FOCUS_RING = "#3B82F6"  # Focus outline (blue-500)

        # Accent (blue for trust)
        ACCENT = "#3B82F6"  # Primary actions (blue-500)
        ACCENT_HOVER = "#2563EB"  # Accent hover (blue-600)
        ACCENT_MUTED = "#DBEAFE"  # Accent background (blue-100)

        # Semantic colors
        SUCCESS = "#22C55E"  # Success states (green-500)
        SUCCESS_MUTED = "#DCFCE7"  # Success background (green-100)
        WARNING = "#F59E0B"  # Warnings (amber-500)
        WARNING_MUTED = "#FEF3C7"  # Warning background (amber-100)
        ERROR = "#EF4444"  # Errors (red-500)
        ERROR_MUTED = "#FEE2E2"  # Error background (red-100)

        # Special
        UNREAD_DOT = "#3B82F6"  # Unread indicator
        STAR_ACTIVE = "#F59E0B"  # Starred state (amber)
        STAR_INACTIVE = "#CBD5E1"  # Unstarred (slate-300)

    class Dark:
        """Dark mode colors."""

        # Background layers
        BG_PRIMARY = "#0F172A"  # slate-900
        BG_SECONDARY = "#1E293B"  # slate-800
        BG_TERTIARY = "#334155"  # slate-700
        BG_ELEVATED = "#1E293B"

        # Text hierarchy
        TEXT_PRIMARY = "#F8FAFC"  # slate-50
        TEXT_SECONDARY = "#CBD5E1"  # slate-300
        TEXT_TERTIARY = "#64748B"  # slate-500
        TEXT_DISABLED = "#475569"  # slate-600

        # Borders
        BORDER_DEFAULT = "#334155"  # slate-700
        BORDER_SUBTLE = "#1E293B"  # slate-800
        BORDER_STRONG = "#475569"  # slate-600

        # Interactive states
        HOVER = "#1E293B"
        ACTIVE = "#334155"
        FOCUS_RING = "#60A5FA"  # blue-400

        # Accent
        ACCENT = "#60A5FA"  # blue-400
        ACCENT_HOVER = "#3B82F6"  # blue-500
        ACCENT_MUTED = "#1E3A5F"  # dark blue bg

        # Semantic
        SUCCESS = "#4ADE80"  # green-400
        SUCCESS_MUTED = "#14532D"  # green-900
        WARNING = "#FBBF24"  # amber-400
        WARNING_MUTED = "#78350F"  # amber-900
        ERROR = "#F87171"  # red-400
        ERROR_MUTED = "#7F1D1D"  # red-900

        # Special
        UNREAD_DOT = "#60A5FA"
        STAR_ACTIVE = "#FBBF24"
        STAR_INACTIVE = "#475569"


class Shadows:
    """Layered shadow system for premium depth."""

    NONE = "none"

    # Subtle elevation
    SM = "0 1px 2px rgba(0,0,0,0.04), 0 1px 3px rgba(0,0,0,0.06)"

    # Medium elevation (cards)
    MD = "0 2px 4px rgba(0,0,0,0.04), 0 4px 8px rgba(0,0,0,0.06)"

    # High elevation (dropdowns, modals)
    LG = "0 4px 8px rgba(0,0,0,0.04), 0 8px 16px rgba(0,0,0,0.06), 0 16px 32px rgba(0,0,0,0.04)"

    # Card-specific (with border simulation)
    CARD = "0 0 0 1px rgba(0,0,0,0.03), 0 1px 3px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.04)"

    # Hover state elevation
    CARD_HOVER = "0 0 0 1px rgba(0,0,0,0.03), 0 4px 8px rgba(0,0,0,0.08), 0 8px 16px rgba(0,0,0,0.04)"


class Animation:
    """Animation timing constants."""

    # Durations (in ms)
    FAST = 100
    NORMAL = 150
    SLOW = 250

    # Easing
    EASE_OUT = "cubic-bezier(0.25, 1, 0.5, 1)"
    EASE_IN_OUT = "cubic-bezier(0.4, 0, 0.2, 1)"
