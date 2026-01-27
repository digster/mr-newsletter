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
from src.ui.themes.theme_schema import ThemeSchema

logger = logging.getLogger(__name__)

# Built-in theme names (cannot be deleted)
BUILTIN_THEMES = frozenset({
    # Original themes
    "default.json",
    "dark-slate.json",
    "light-clean.json",
    "midnight.json",
    # Popular color schemes
    "nord.json",
    "solarized-light.json",
    "solarized-dark.json",
    "dracula.json",
    "gruvbox-light.json",
    "gruvbox-dark.json",
    "catppuccin-latte.json",
    "catppuccin-mocha.json",
    "one-dark.json",
    "tokyo-night.json",
    # Glass effects
    "liquid-glass.json",
})


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
        from src.ui.themes.builtin_themes import ALL_BUILTIN_THEMES

        for filename, theme_data in ALL_BUILTIN_THEMES.items():
            theme_path = self._themes_dir / filename
            if not theme_path.exists():
                theme_path.write_text(json.dumps(theme_data, indent=2))
                logger.info(f"Created built-in theme at {theme_path}")

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

    def import_theme_from_bytes(
        self, filename: str, content: bytes
    ) -> tuple[bool, Optional[str]]:
        """Import a theme from bytes content (for web mode).

        In web browsers, file picker doesn't expose local file paths.
        Instead, we receive the file content as bytes directly.

        Args:
            filename: Original filename from the file picker.
            content: JSON content as bytes.

        Returns:
            Tuple of (success, error_message).
        """
        try:
            # Parse and validate
            data = json.loads(content.decode("utf-8"))
            success, theme, error = self.validate_theme(data)
            if not success:
                return False, error

            # Generate destination path
            dest_filename = filename if filename.endswith(".json") else f"{filename}.json"
            dest_path = self._themes_dir / dest_filename
            counter = 1

            while dest_path.exists() and dest_filename not in BUILTIN_THEMES:
                stem = Path(filename).stem
                dest_filename = f"{stem}_{counter}.json"
                dest_path = self._themes_dir / dest_filename
                counter += 1

            # Cannot overwrite built-in themes
            if dest_filename in BUILTIN_THEMES:
                dest_filename = f"custom_{dest_filename}"
                dest_path = self._themes_dir / dest_filename

            # Write content
            dest_path.write_bytes(content)
            logger.info(f"Imported theme from bytes: {dest_filename}")
            return True, None

        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}"
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
