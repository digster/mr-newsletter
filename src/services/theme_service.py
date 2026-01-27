"""Theme service for managing application themes.

Handles loading, validating, applying, importing, and exporting themes.
Includes built-in theme generation and persistence.
"""

import json
import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Type

from pydantic import ValidationError

from src.config.settings import get_settings
from src.ui.themes.design_tokens import Colors, set_active_theme_colors
from src.ui.themes.dynamic_colors import create_colors_from_theme
from src.ui.themes.theme_schema import (
    ThemeColorSet,
    ThemeColors,
    ThemeMetadata,
    ThemeSchema,
)

logger = logging.getLogger(__name__)

# Built-in theme names (cannot be deleted)
BUILTIN_THEMES = frozenset({"default.json", "dark-slate.json", "light-clean.json", "midnight.json"})


@dataclass
class ThemeInfo:
    """Theme information for display in UI."""

    filename: str
    name: str
    description: Optional[str]
    author: Optional[str]
    base: str
    is_builtin: bool
    preview_colors: tuple[str, str, str]  # (bg_primary, accent, text_primary)


class ThemeService:
    """Service for managing application themes."""

    def __init__(self):
        """Initialize theme service."""
        self.settings = get_settings()
        self._themes_dir = self.settings.user_data_dir / "themes"
        self._ensure_themes_directory()
        self._ensure_builtin_themes()

    @property
    def themes_dir(self) -> Path:
        """Get themes directory path."""
        return self._themes_dir

    def _ensure_themes_directory(self) -> None:
        """Ensure the themes directory exists."""
        self._themes_dir.mkdir(parents=True, exist_ok=True)

    def _ensure_builtin_themes(self) -> None:
        """Create built-in themes if they don't exist."""
        default_path = self._themes_dir / "default.json"
        dark_slate_path = self._themes_dir / "dark-slate.json"
        light_clean_path = self._themes_dir / "light-clean.json"
        midnight_path = self._themes_dir / "midnight.json"

        if not default_path.exists():
            self._write_default_theme(default_path)

        if not dark_slate_path.exists():
            self._write_dark_slate_theme(dark_slate_path)

        if not light_clean_path.exists():
            self._write_light_clean_theme(light_clean_path)

        if not midnight_path.exists():
            self._write_midnight_theme(midnight_path)

    def _write_default_theme(self, path: Path) -> None:
        """Write the default theme file from current Colors."""
        theme_data = {
            "metadata": {
                "name": "Default",
                "author": "Newsletter Reader",
                "version": "1.0.0",
                "description": "Sophistication & Trust - cool slate tones with blue accent",
                "base": "light",
            },
            "colors": {
                "light": self._colors_class_to_dict(Colors.Light),
                "dark": self._colors_class_to_dict(Colors.Dark),
            },
        }
        path.write_text(json.dumps(theme_data, indent=2))
        logger.info(f"Created default theme at {path}")

    def _write_dark_slate_theme(self, path: Path) -> None:
        """Write the dark slate theme file (OLED-friendly)."""
        theme_data = {
            "metadata": {
                "name": "Dark Slate",
                "author": "Newsletter Reader",
                "version": "1.0.0",
                "description": "Deep slate OLED-optimized dark theme",
                "base": "dark",
            },
            "colors": {
                "light": {
                    "bg_primary": "#FAFAFA",
                    "bg_secondary": "#F5F5F5",
                    "bg_tertiary": "#EEEEEE",
                    "bg_elevated": "#FFFFFF",
                    "text_primary": "#1A1A1A",
                    "text_secondary": "#525252",
                    "text_tertiary": "#8A8A8A",
                    "text_disabled": "#BDBDBD",
                    "border_default": "#E0E0E0",
                    "border_subtle": "#EEEEEE",
                    "border_strong": "#BDBDBD",
                    "hover": "#F5F5F5",
                    "active": "#EEEEEE",
                    "focus_ring": "#6366F1",
                    "accent": "#6366F1",
                    "accent_hover": "#4F46E5",
                    "accent_muted": "#EEF2FF",
                    "success": "#22C55E",
                    "success_muted": "#DCFCE7",
                    "warning": "#F59E0B",
                    "warning_muted": "#FEF3C7",
                    "error": "#EF4444",
                    "error_muted": "#FEE2E2",
                    "unread_dot": "#6366F1",
                    "star_active": "#F59E0B",
                    "star_inactive": "#BDBDBD",
                },
                "dark": {
                    "bg_primary": "#000000",
                    "bg_secondary": "#0A0A0A",
                    "bg_tertiary": "#171717",
                    "bg_elevated": "#0A0A0A",
                    "text_primary": "#FAFAFA",
                    "text_secondary": "#A3A3A3",
                    "text_tertiary": "#737373",
                    "text_disabled": "#525252",
                    "border_default": "#262626",
                    "border_subtle": "#171717",
                    "border_strong": "#404040",
                    "hover": "#0A0A0A",
                    "active": "#171717",
                    "focus_ring": "#818CF8",
                    "accent": "#818CF8",
                    "accent_hover": "#6366F1",
                    "accent_muted": "#1E1B4B",
                    "success": "#4ADE80",
                    "success_muted": "#14532D",
                    "warning": "#FBBF24",
                    "warning_muted": "#78350F",
                    "error": "#F87171",
                    "error_muted": "#7F1D1D",
                    "unread_dot": "#818CF8",
                    "star_active": "#FBBF24",
                    "star_inactive": "#404040",
                },
            },
        }
        path.write_text(json.dumps(theme_data, indent=2))
        logger.info(f"Created dark-slate theme at {path}")

    def _write_light_clean_theme(self, path: Path) -> None:
        """Write the light clean theme file (warm, modern, minimal)."""
        theme_data = {
            "metadata": {
                "name": "Light Clean",
                "author": "Newsletter Reader",
                "version": "1.0.0",
                "description": "Warm, modern light theme with teal accent",
                "base": "light",
            },
            "colors": {
                "light": {
                    "bg_primary": "#FFFFFF",
                    "bg_secondary": "#F8FAFC",
                    "bg_tertiary": "#F1F5F9",
                    "bg_elevated": "#FFFFFF",
                    "text_primary": "#0F172A",
                    "text_secondary": "#475569",
                    "text_tertiary": "#94A3B8",
                    "text_disabled": "#CBD5E1",
                    "border_default": "#E2E8F0",
                    "border_subtle": "#F1F5F9",
                    "border_strong": "#CBD5E1",
                    "hover": "#F8FAFC",
                    "active": "#F1F5F9",
                    "focus_ring": "#14B8A6",
                    "accent": "#14B8A6",
                    "accent_hover": "#0D9488",
                    "accent_muted": "#CCFBF1",
                    "success": "#10B981",
                    "success_muted": "#D1FAE5",
                    "warning": "#F59E0B",
                    "warning_muted": "#FEF3C7",
                    "error": "#EF4444",
                    "error_muted": "#FEE2E2",
                    "unread_dot": "#14B8A6",
                    "star_active": "#F59E0B",
                    "star_inactive": "#CBD5E1",
                },
                "dark": {
                    "bg_primary": "#0F172A",
                    "bg_secondary": "#1E293B",
                    "bg_tertiary": "#334155",
                    "bg_elevated": "#1E293B",
                    "text_primary": "#F8FAFC",
                    "text_secondary": "#CBD5E1",
                    "text_tertiary": "#94A3B8",
                    "text_disabled": "#64748B",
                    "border_default": "#334155",
                    "border_subtle": "#1E293B",
                    "border_strong": "#475569",
                    "hover": "#1E293B",
                    "active": "#334155",
                    "focus_ring": "#2DD4BF",
                    "accent": "#2DD4BF",
                    "accent_hover": "#14B8A6",
                    "accent_muted": "#134E4A",
                    "success": "#34D399",
                    "success_muted": "#065F46",
                    "warning": "#FBBF24",
                    "warning_muted": "#78350F",
                    "error": "#F87171",
                    "error_muted": "#7F1D1D",
                    "unread_dot": "#2DD4BF",
                    "star_active": "#FBBF24",
                    "star_inactive": "#475569",
                },
            },
        }
        path.write_text(json.dumps(theme_data, indent=2))
        logger.info(f"Created light-clean theme at {path}")

    def _write_midnight_theme(self, path: Path) -> None:
        """Write the midnight theme file (dramatic dark with magenta accent)."""
        theme_data = {
            "metadata": {
                "name": "Midnight",
                "author": "Newsletter Reader",
                "version": "1.0.0",
                "description": "Dramatic dark theme with magenta/fuchsia accent",
                "base": "dark",
            },
            "colors": {
                "light": {
                    # Light mode variant (inverted approach)
                    "bg_primary": "#FDFAFF",
                    "bg_secondary": "#F8F0FC",
                    "bg_tertiary": "#F3E8FA",
                    "bg_elevated": "#FFFFFF",
                    "text_primary": "#1A0A24",
                    "text_secondary": "#4A3456",
                    "text_tertiary": "#8B6A9E",
                    "text_disabled": "#C4A8D4",
                    "border_default": "#E8D4F0",
                    "border_subtle": "#F3E8FA",
                    "border_strong": "#D4B8E4",
                    "hover": "#F8F0FC",
                    "active": "#F3E8FA",
                    "focus_ring": "#D946EF",
                    "accent": "#D946EF",
                    "accent_hover": "#C026D3",
                    "accent_muted": "#FAE8FF",
                    "success": "#22C55E",
                    "success_muted": "#DCFCE7",
                    "warning": "#F59E0B",
                    "warning_muted": "#FEF3C7",
                    "error": "#EF4444",
                    "error_muted": "#FEE2E2",
                    "unread_dot": "#D946EF",
                    "star_active": "#F59E0B",
                    "star_inactive": "#C4A8D4",
                },
                "dark": {
                    # True black OLED with magenta/fuchsia accent
                    "bg_primary": "#0D0D0D",
                    "bg_secondary": "#141414",
                    "bg_tertiary": "#1F1F1F",
                    "bg_elevated": "#181818",
                    "text_primary": "#FAFAFA",
                    "text_secondary": "#B8B8B8",
                    "text_tertiary": "#787878",
                    "text_disabled": "#484848",
                    "border_default": "#2E2E2E",
                    "border_subtle": "#1F1F1F",
                    "border_strong": "#444444",
                    "hover": "#1A1A1A",
                    "active": "#252525",
                    "focus_ring": "#E879F9",
                    "accent": "#E879F9",
                    "accent_hover": "#D946EF",
                    "accent_muted": "#3B0764",
                    "success": "#4ADE80",
                    "success_muted": "#14532D",
                    "warning": "#FBBF24",
                    "warning_muted": "#78350F",
                    "error": "#F87171",
                    "error_muted": "#7F1D1D",
                    "unread_dot": "#E879F9",
                    "star_active": "#FBBF24",
                    "star_inactive": "#444444",
                },
            },
        }
        path.write_text(json.dumps(theme_data, indent=2))
        logger.info(f"Created midnight theme at {path}")

    def _colors_class_to_dict(self, colors_class: Type) -> dict:
        """Convert a Colors class to a dictionary.

        Args:
            colors_class: Colors.Light or Colors.Dark class.

        Returns:
            Dictionary with color values (snake_case keys).
        """
        result = {}
        for attr in dir(colors_class):
            if not attr.startswith("_") and attr.isupper():
                # Convert UPPER_SNAKE to lower_snake
                key = attr.lower()
                result[key] = getattr(colors_class, attr)
        return result

    def list_themes(self) -> list[ThemeInfo]:
        """List all available themes.

        Returns:
            List of ThemeInfo objects sorted with built-ins first.
        """
        themes = []

        for theme_file in self._themes_dir.glob("*.json"):
            try:
                success, theme, _ = self.load_theme(theme_file.name)
                if success and theme:
                    # Get preview colors (using light mode for preview)
                    light_colors = theme.colors.light if theme.colors else None
                    preview = (
                        getattr(light_colors, "bg_primary", None) or Colors.Light.BG_PRIMARY,
                        getattr(light_colors, "accent", None) or Colors.Light.ACCENT,
                        getattr(light_colors, "text_primary", None) or Colors.Light.TEXT_PRIMARY,
                    )

                    themes.append(
                        ThemeInfo(
                            filename=theme_file.name,
                            name=theme.metadata.name,
                            description=theme.metadata.description,
                            author=theme.metadata.author,
                            base=theme.metadata.base,
                            is_builtin=theme_file.name in BUILTIN_THEMES,
                            preview_colors=preview,
                        )
                    )
            except Exception as e:
                logger.warning(f"Failed to load theme {theme_file.name}: {e}")
                continue

        # Sort: built-ins first, then by name
        themes.sort(key=lambda t: (not t.is_builtin, t.name.lower()))
        return themes

    def load_theme(self, filename: str) -> tuple[bool, Optional[ThemeSchema], Optional[str]]:
        """Load and validate a theme file.

        Args:
            filename: Theme filename (e.g., 'default.json').

        Returns:
            Tuple of (success, theme_schema, error_message).
        """
        theme_path = self._themes_dir / filename

        if not theme_path.exists():
            return False, None, f"Theme file not found: {filename}"

        try:
            with open(theme_path, encoding="utf-8") as f:
                data = json.load(f)

            theme = ThemeSchema.model_validate(data)
            return True, theme, None

        except json.JSONDecodeError as e:
            return False, None, f"Invalid JSON: {e}"
        except ValidationError as e:
            return False, None, f"Validation error: {e}"
        except Exception as e:
            return False, None, f"Error loading theme: {e}"

    def validate_theme(self, data: dict) -> tuple[bool, Optional[ThemeSchema], Optional[str]]:
        """Validate theme data against schema.

        Args:
            data: Theme data dictionary.

        Returns:
            Tuple of (success, theme_schema, error_message).
        """
        try:
            theme = ThemeSchema.model_validate(data)
            return True, theme, None
        except ValidationError as e:
            return False, None, f"Validation error: {e}"

    def apply_theme(self, theme: ThemeSchema) -> tuple[Type, Type]:
        """Apply a theme by generating and setting color classes.

        Args:
            theme: Validated theme schema.

        Returns:
            Tuple of (light_colors_class, dark_colors_class).
        """
        light_colors, dark_colors = create_colors_from_theme(theme)
        set_active_theme_colors(light_colors, dark_colors)
        logger.info(f"Applied theme: {theme.metadata.name}")
        return light_colors, dark_colors

    def import_theme(self, source_path: Path) -> tuple[bool, Optional[str]]:
        """Import a theme file from external location.

        Args:
            source_path: Path to the theme JSON file.

        Returns:
            Tuple of (success, error_message).
        """
        if not source_path.exists():
            return False, "Source file does not exist"

        if not source_path.suffix.lower() == ".json":
            return False, "Theme file must be a JSON file"

        try:
            # Validate before importing
            with open(source_path, encoding="utf-8") as f:
                data = json.load(f)

            success, theme, error = self.validate_theme(data)
            if not success:
                return False, error

            # Generate unique filename if needed
            dest_filename = source_path.name
            dest_path = self._themes_dir / dest_filename
            counter = 1

            while dest_path.exists() and dest_filename not in BUILTIN_THEMES:
                stem = source_path.stem
                dest_filename = f"{stem}_{counter}.json"
                dest_path = self._themes_dir / dest_filename
                counter += 1

            # Cannot overwrite built-in themes
            if dest_filename in BUILTIN_THEMES:
                dest_filename = f"custom_{dest_filename}"
                dest_path = self._themes_dir / dest_filename

            shutil.copy2(source_path, dest_path)
            logger.info(f"Imported theme: {dest_filename}")
            return True, None

        except json.JSONDecodeError as e:
            return False, f"Invalid JSON file: {e}"
        except Exception as e:
            return False, f"Import failed: {e}"

    def export_theme(self, filename: str, dest_path: Path) -> tuple[bool, Optional[str]]:
        """Export a theme file to external location.

        Args:
            filename: Theme filename to export.
            dest_path: Destination path for the exported file.

        Returns:
            Tuple of (success, error_message).
        """
        source_path = self._themes_dir / filename

        if not source_path.exists():
            return False, f"Theme not found: {filename}"

        try:
            shutil.copy2(source_path, dest_path)
            logger.info(f"Exported theme {filename} to {dest_path}")
            return True, None
        except Exception as e:
            return False, f"Export failed: {e}"

    def delete_theme(self, filename: str) -> tuple[bool, Optional[str]]:
        """Delete a custom theme file.

        Args:
            filename: Theme filename to delete.

        Returns:
            Tuple of (success, error_message).
        """
        if filename in BUILTIN_THEMES:
            return False, "Cannot delete built-in themes"

        theme_path = self._themes_dir / filename

        if not theme_path.exists():
            return False, f"Theme not found: {filename}"

        try:
            theme_path.unlink()
            logger.info(f"Deleted theme: {filename}")
            return True, None
        except Exception as e:
            return False, f"Delete failed: {e}"

    def get_theme_as_json(self, filename: str) -> tuple[bool, Optional[str], Optional[str]]:
        """Get theme file contents as JSON string.

        Args:
            filename: Theme filename.

        Returns:
            Tuple of (success, json_content, error_message).
        """
        theme_path = self._themes_dir / filename

        if not theme_path.exists():
            return False, None, f"Theme not found: {filename}"

        try:
            content = theme_path.read_text(encoding="utf-8")
            # Re-format for consistent output
            data = json.loads(content)
            formatted = json.dumps(data, indent=2)
            return True, formatted, None
        except Exception as e:
            return False, None, f"Error reading theme: {e}"

    def create_theme_from_current(
        self,
        name: str,
        description: Optional[str] = None,
        author: Optional[str] = None,
    ) -> tuple[bool, Optional[str], Optional[str]]:
        """Create a new theme file from current active colors.

        Args:
            name: Theme name.
            description: Optional description.
            author: Optional author name.

        Returns:
            Tuple of (success, filename, error_message).
        """
        from src.ui.themes.design_tokens import get_active_theme_colors

        light_colors, dark_colors = get_active_theme_colors()

        # Use defaults if no active theme
        if light_colors is None:
            light_colors = Colors.Light
        if dark_colors is None:
            dark_colors = Colors.Dark

        theme_data = {
            "metadata": {
                "name": name,
                "author": author,
                "version": "1.0.0",
                "description": description,
                "base": "light",
            },
            "colors": {
                "light": self._colors_class_to_dict(light_colors),
                "dark": self._colors_class_to_dict(dark_colors),
            },
        }

        # Generate safe filename
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name.lower())
        filename = f"{safe_name}.json"
        dest_path = self._themes_dir / filename

        counter = 1
        while dest_path.exists():
            filename = f"{safe_name}_{counter}.json"
            dest_path = self._themes_dir / filename
            counter += 1

        try:
            dest_path.write_text(json.dumps(theme_data, indent=2), encoding="utf-8")
            logger.info(f"Created theme: {filename}")
            return True, filename, None
        except Exception as e:
            return False, None, f"Failed to create theme: {e}"
