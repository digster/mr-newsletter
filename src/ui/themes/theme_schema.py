"""Theme schema for validating theme JSON structure.

Pydantic models that define the structure of theme files with validation
and fallback defaults.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ThemeMetadata(BaseModel):
    """Theme metadata information."""

    name: str = Field(default="Custom Theme", description="Theme display name")
    author: Optional[str] = Field(default=None, description="Theme author name")
    version: str = Field(default="1.0.0", description="Theme version")
    description: Optional[str] = Field(default=None, description="Theme description")
    base: str = Field(default="light", description="Base theme mode (light/dark)")

    @field_validator("base")
    @classmethod
    def validate_base(cls, v: str) -> str:
        """Validate base theme mode."""
        if v not in ("light", "dark"):
            return "light"
        return v


class ThemeColorSet(BaseModel):
    """Color tokens for a single theme mode (light or dark)."""

    # Background layers
    bg_primary: Optional[str] = Field(default=None, description="Main background")
    bg_secondary: Optional[str] = Field(default=None, description="Subtle alternate background")
    bg_tertiary: Optional[str] = Field(default=None, description="Cards hover, containers")
    bg_elevated: Optional[str] = Field(default=None, description="Modals, dropdowns")

    # Text hierarchy
    text_primary: Optional[str] = Field(default=None, description="Headlines, primary text")
    text_secondary: Optional[str] = Field(default=None, description="Body text")
    text_tertiary: Optional[str] = Field(default=None, description="Captions, hints")
    text_disabled: Optional[str] = Field(default=None, description="Disabled text")

    # Borders
    border_default: Optional[str] = Field(default=None, description="Standard borders")
    border_subtle: Optional[str] = Field(default=None, description="Subtle dividers")
    border_strong: Optional[str] = Field(default=None, description="Emphasized borders")

    # Interactive states
    hover: Optional[str] = Field(default=None, description="Hover background")
    active: Optional[str] = Field(default=None, description="Active/pressed state")
    focus_ring: Optional[str] = Field(default=None, description="Focus outline")

    # Accent
    accent: Optional[str] = Field(default=None, description="Primary actions color")
    accent_hover: Optional[str] = Field(default=None, description="Accent hover state")
    accent_muted: Optional[str] = Field(default=None, description="Accent background")

    # Semantic colors
    success: Optional[str] = Field(default=None, description="Success states")
    success_muted: Optional[str] = Field(default=None, description="Success background")
    warning: Optional[str] = Field(default=None, description="Warnings")
    warning_muted: Optional[str] = Field(default=None, description="Warning background")
    error: Optional[str] = Field(default=None, description="Errors")
    error_muted: Optional[str] = Field(default=None, description="Error background")

    # Special
    unread_dot: Optional[str] = Field(default=None, description="Unread indicator")
    star_active: Optional[str] = Field(default=None, description="Starred state")
    star_inactive: Optional[str] = Field(default=None, description="Unstarred state")

    @field_validator("*", mode="before")
    @classmethod
    def validate_color(cls, v):
        """Validate color format (hex colors)."""
        if v is None:
            return None
        if isinstance(v, str) and (v.startswith("#") or v.startswith("rgb")):
            return v
        return None


class ThemeColors(BaseModel):
    """Color configuration for both light and dark modes."""

    light: Optional[ThemeColorSet] = Field(default=None, description="Light mode colors")
    dark: Optional[ThemeColorSet] = Field(default=None, description="Dark mode colors")


class ThemeTypography(BaseModel):
    """Typography configuration."""

    font_family: Optional[str] = Field(default=None, description="Primary font family")

    # Headlines
    h1_size: Optional[int] = Field(default=None, ge=12, le=72, description="H1 size")
    h2_size: Optional[int] = Field(default=None, ge=10, le=60, description="H2 size")
    h3_size: Optional[int] = Field(default=None, ge=10, le=48, description="H3 size")
    h4_size: Optional[int] = Field(default=None, ge=10, le=36, description="H4 size")

    # Body
    body_size: Optional[int] = Field(default=None, ge=10, le=24, description="Body size")
    body_small_size: Optional[int] = Field(default=None, ge=10, le=20, description="Small body")
    caption_size: Optional[int] = Field(default=None, ge=8, le=18, description="Caption size")

    # Weights
    weight_bold: Optional[int] = Field(default=None, ge=100, le=900, description="Bold weight")
    weight_medium: Optional[int] = Field(default=None, ge=100, le=900, description="Medium weight")
    weight_regular: Optional[int] = Field(default=None, ge=100, le=900, description="Regular weight")


class ThemeSpacing(BaseModel):
    """Spacing tokens (4px grid system)."""

    none: Optional[int] = Field(default=None, ge=0, description="No spacing")
    xxs: Optional[int] = Field(default=None, ge=0, description="Extra extra small")
    xs: Optional[int] = Field(default=None, ge=0, description="Extra small")
    sm: Optional[int] = Field(default=None, ge=0, description="Small")
    md: Optional[int] = Field(default=None, ge=0, description="Medium")
    lg: Optional[int] = Field(default=None, ge=0, description="Large")
    xl: Optional[int] = Field(default=None, ge=0, description="Extra large")
    xxl: Optional[int] = Field(default=None, ge=0, description="Extra extra large")


class ThemeBorderRadius(BaseModel):
    """Border radius tokens."""

    none: Optional[int] = Field(default=None, ge=0, description="No radius")
    sm: Optional[int] = Field(default=None, ge=0, description="Small radius")
    md: Optional[int] = Field(default=None, ge=0, description="Medium radius")
    lg: Optional[int] = Field(default=None, ge=0, description="Large radius")
    full: Optional[int] = Field(default=None, ge=0, description="Full/pill radius")


class ThemeShadows(BaseModel):
    """Shadow definitions."""

    none: Optional[str] = Field(default=None, description="No shadow")
    sm: Optional[str] = Field(default=None, description="Small shadow")
    md: Optional[str] = Field(default=None, description="Medium shadow")
    lg: Optional[str] = Field(default=None, description="Large shadow")
    card: Optional[str] = Field(default=None, description="Card shadow")
    card_hover: Optional[str] = Field(default=None, description="Card hover shadow")


class ThemeAnimation(BaseModel):
    """Animation timing constants."""

    fast: Optional[int] = Field(default=None, ge=0, le=1000, description="Fast duration (ms)")
    normal: Optional[int] = Field(default=None, ge=0, le=2000, description="Normal duration (ms)")
    slow: Optional[int] = Field(default=None, ge=0, le=3000, description="Slow duration (ms)")


class SidebarOverrides(BaseModel):
    """Sidebar-specific overrides."""

    bg: Optional[str] = Field(default=None, description="Sidebar background")
    width: Optional[int] = Field(default=None, ge=100, le=500, description="Sidebar width")


class CardOverrides(BaseModel):
    """Card-specific overrides."""

    bg: Optional[str] = Field(default=None, description="Card background")
    shadow: Optional[str] = Field(default=None, description="Card shadow")


class EmailOverrides(BaseModel):
    """Email-specific overrides."""

    unread_bg: Optional[str] = Field(default=None, description="Unread email background")


class DialogOverrides(BaseModel):
    """Dialog-specific overrides."""

    bg: Optional[str] = Field(default=None, description="Dialog background")


class ThemeSectionOverrides(BaseModel):
    """Section-specific overrides."""

    sidebar: Optional[SidebarOverrides] = Field(default=None, description="Sidebar overrides")
    cards: Optional[CardOverrides] = Field(default=None, description="Card overrides")
    emails: Optional[EmailOverrides] = Field(default=None, description="Email overrides")
    dialogs: Optional[DialogOverrides] = Field(default=None, description="Dialog overrides")


class ThemeSchema(BaseModel):
    """Complete theme schema for validation."""

    model_config = ConfigDict(extra="ignore")  # Ignore extra fields in JSON

    metadata: ThemeMetadata = Field(default_factory=ThemeMetadata, description="Theme metadata")
    colors: Optional[ThemeColors] = Field(default=None, description="Color configuration")
    typography: Optional[ThemeTypography] = Field(default=None, description="Typography settings")
    spacing: Optional[ThemeSpacing] = Field(default=None, description="Spacing tokens")
    border_radius: Optional[ThemeBorderRadius] = Field(default=None, description="Border radius")
    shadows: Optional[ThemeShadows] = Field(default=None, description="Shadow definitions")
    animation: Optional[ThemeAnimation] = Field(default=None, description="Animation timings")
    section_overrides: Optional[ThemeSectionOverrides] = Field(
        default=None, description="Section-specific overrides"
    )
