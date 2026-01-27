"""Unit tests for ThemeService."""

import json
import re
import tempfile
from pathlib import Path

import pytest

from src.services.theme_service import BUILTIN_THEMES, ThemeService
from src.ui.themes.builtin_themes import ALL_BUILTIN_THEMES
from src.ui.themes.design_tokens import Colors
from src.ui.themes.dynamic_colors import create_colors_from_theme
from src.ui.themes.theme_schema import ThemeColorSet, ThemeColors, ThemeMetadata, ThemeSchema

# All required color tokens that each theme must define
REQUIRED_COLOR_TOKENS = [
    "bg_primary",
    "bg_secondary",
    "bg_tertiary",
    "bg_elevated",
    "text_primary",
    "text_secondary",
    "text_tertiary",
    "text_disabled",
    "border_default",
    "border_subtle",
    "border_strong",
    "hover",
    "active",
    "focus_ring",
    "accent",
    "accent_hover",
    "accent_muted",
    "success",
    "success_muted",
    "warning",
    "warning_muted",
    "error",
    "error_muted",
    "unread_dot",
    "star_active",
    "star_inactive",
]


class TestThemeSchema:
    """Tests for theme schema validation."""

    def test_valid_minimal_theme(self):
        """Test validating a minimal valid theme."""
        data = {
            "metadata": {
                "name": "Test Theme",
            }
        }
        theme = ThemeSchema.model_validate(data)
        assert theme.metadata.name == "Test Theme"
        assert theme.metadata.base == "light"  # default
        assert theme.colors is None

    def test_valid_full_theme(self):
        """Test validating a complete theme."""
        data = {
            "metadata": {
                "name": "Full Theme",
                "author": "Test Author",
                "version": "1.0.0",
                "description": "A test theme",
                "base": "dark",
            },
            "colors": {
                "light": {
                    "bg_primary": "#FFFFFF",
                    "accent": "#3B82F6",
                },
                "dark": {
                    "bg_primary": "#1A1A1A",
                    "accent": "#60A5FA",
                },
            },
        }
        theme = ThemeSchema.model_validate(data)
        assert theme.metadata.name == "Full Theme"
        assert theme.metadata.base == "dark"
        assert theme.colors.light.bg_primary == "#FFFFFF"
        assert theme.colors.dark.accent == "#60A5FA"

    def test_invalid_base_falls_back_to_light(self):
        """Test that invalid base value falls back to light."""
        data = {
            "metadata": {
                "name": "Test",
                "base": "invalid",
            }
        }
        theme = ThemeSchema.model_validate(data)
        assert theme.metadata.base == "light"

    def test_invalid_color_is_none(self):
        """Test that invalid color values become None."""
        data = {
            "metadata": {"name": "Test"},
            "colors": {
                "light": {
                    "bg_primary": "not-a-color",
                    "accent": "#3B82F6",
                }
            },
        }
        theme = ThemeSchema.model_validate(data)
        # Invalid color should be None, valid color should remain
        assert theme.colors.light.bg_primary is None
        assert theme.colors.light.accent == "#3B82F6"

    def test_extra_fields_ignored(self):
        """Test that extra fields in JSON are ignored."""
        data = {
            "metadata": {"name": "Test"},
            "unknown_field": "should be ignored",
            "colors": {
                "light": {
                    "bg_primary": "#FFFFFF",
                    "custom_color": "#000000",  # Not in schema
                }
            },
        }
        theme = ThemeSchema.model_validate(data)
        assert theme.metadata.name == "Test"
        assert not hasattr(theme, "unknown_field")


class TestDynamicColors:
    """Tests for dynamic color class generation."""

    def test_create_colors_with_full_theme(self):
        """Test creating colors from a complete theme."""
        data = {
            "metadata": {"name": "Test"},
            "colors": {
                "light": {
                    "bg_primary": "#FAFAFA",
                    "accent": "#FF0000",
                },
                "dark": {
                    "bg_primary": "#1A1A1A",
                    "accent": "#00FF00",
                },
            },
        }
        theme = ThemeSchema.model_validate(data)
        light, dark = create_colors_from_theme(theme)

        assert light.BG_PRIMARY == "#FAFAFA"
        assert light.ACCENT == "#FF0000"
        assert dark.BG_PRIMARY == "#1A1A1A"
        assert dark.ACCENT == "#00FF00"

    def test_create_colors_falls_back_to_defaults(self):
        """Test that missing colors fall back to defaults."""
        data = {
            "metadata": {"name": "Test"},
            "colors": {
                "light": {
                    "accent": "#FF0000",
                    # bg_primary not specified - should use default
                },
            },
        }
        theme = ThemeSchema.model_validate(data)
        light, dark = create_colors_from_theme(theme)

        # Custom value
        assert light.ACCENT == "#FF0000"
        # Fallback to default
        assert light.BG_PRIMARY == Colors.Light.BG_PRIMARY
        # Dark mode should fully fall back since not specified
        assert dark.BG_PRIMARY == Colors.Dark.BG_PRIMARY

    def test_create_colors_with_empty_theme(self):
        """Test creating colors from a theme with no color specifications."""
        data = {"metadata": {"name": "Empty"}}
        theme = ThemeSchema.model_validate(data)
        light, dark = create_colors_from_theme(theme)

        # All values should match defaults
        assert light.BG_PRIMARY == Colors.Light.BG_PRIMARY
        assert light.ACCENT == Colors.Light.ACCENT
        assert dark.BG_PRIMARY == Colors.Dark.BG_PRIMARY
        assert dark.ACCENT == Colors.Dark.ACCENT


class TestThemeService:
    """Tests for ThemeService."""

    @pytest.fixture
    def temp_themes_dir(self, tmp_path):
        """Create a temporary themes directory."""
        themes_dir = tmp_path / "themes"
        themes_dir.mkdir()
        return themes_dir

    @pytest.fixture
    def service(self, temp_themes_dir, monkeypatch):
        """Create theme service with temp directory."""
        # Create service first
        svc = ThemeService()
        # Override the themes directory
        monkeypatch.setattr(svc, "_themes_dir", temp_themes_dir)
        # Re-run the initialization to create built-ins in temp dir
        svc._ensure_themes_directory()
        svc._ensure_builtin_themes()
        return svc

    def test_ensures_builtin_themes_created(self, service, temp_themes_dir):
        """Test that built-in themes are created."""
        assert (temp_themes_dir / "default.json").exists()
        assert (temp_themes_dir / "dark-slate.json").exists()

    def test_list_themes(self, service):
        """Test listing available themes."""
        themes = service.list_themes()

        assert len(themes) >= 2  # At least built-in themes
        names = [t.name for t in themes]
        assert "Default" in names
        assert "Dark Slate" in names

        # Built-ins should be first
        assert themes[0].is_builtin or themes[1].is_builtin

    def test_load_theme_success(self, service):
        """Test loading a valid theme."""
        success, theme, error = service.load_theme("default.json")

        assert success is True
        assert theme is not None
        assert error is None
        assert theme.metadata.name == "Default"

    def test_load_theme_not_found(self, service):
        """Test loading a non-existent theme."""
        success, theme, error = service.load_theme("nonexistent.json")

        assert success is False
        assert theme is None
        assert "not found" in error.lower()

    def test_validate_theme(self, service):
        """Test validating theme data."""
        valid_data = {
            "metadata": {"name": "Test"},
            "colors": {"light": {"accent": "#FF0000"}},
        }

        success, theme, error = service.validate_theme(valid_data)
        assert success is True
        assert theme is not None
        assert error is None

    def test_apply_theme(self, service):
        """Test applying a theme generates color classes."""
        success, theme, _ = service.load_theme("default.json")
        assert success

        light, dark = service.apply_theme(theme)

        # Check that classes have expected attributes
        assert hasattr(light, "BG_PRIMARY")
        assert hasattr(light, "ACCENT")
        assert hasattr(dark, "BG_PRIMARY")
        assert hasattr(dark, "ACCENT")

    def test_import_theme(self, service, temp_themes_dir):
        """Test importing a theme file."""
        # Create a theme file to import
        import_data = {
            "metadata": {"name": "Imported Theme"},
            "colors": {"light": {"accent": "#123456"}},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(import_data, f)
            import_path = Path(f.name)

        try:
            success, error = service.import_theme(import_path)
            assert success is True
            assert error is None

            # Verify theme was imported
            themes = service.list_themes()
            names = [t.name for t in themes]
            assert "Imported Theme" in names
        finally:
            import_path.unlink()

    def test_import_invalid_json(self, service):
        """Test importing an invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("not valid json")
            import_path = Path(f.name)

        try:
            success, error = service.import_theme(import_path)
            assert success is False
            assert "invalid json" in error.lower()
        finally:
            import_path.unlink()

    def test_export_theme(self, service, temp_themes_dir, tmp_path):
        """Test exporting a theme file."""
        export_path = tmp_path / "exported.json"

        success, error = service.export_theme("default.json", export_path)

        assert success is True
        assert error is None
        assert export_path.exists()

        # Verify exported content is valid
        with open(export_path) as f:
            data = json.load(f)
        assert data["metadata"]["name"] == "Default"

    def test_delete_builtin_theme_fails(self, service):
        """Test that built-in themes cannot be deleted."""
        success, error = service.delete_theme("default.json")

        assert success is False
        assert "built-in" in error.lower()

    def test_delete_custom_theme(self, service, temp_themes_dir):
        """Test deleting a custom theme."""
        # Create a custom theme
        custom_path = temp_themes_dir / "custom.json"
        custom_path.write_text(json.dumps({"metadata": {"name": "Custom"}}))

        success, error = service.delete_theme("custom.json")

        assert success is True
        assert error is None
        assert not custom_path.exists()

    def test_create_theme_from_current(self, service, temp_themes_dir):
        """Test creating a new theme from current colors."""
        success, filename, error = service.create_theme_from_current(
            name="My Custom Theme",
            description="A test theme",
            author="Tester",
        )

        assert success is True
        assert filename is not None
        assert error is None

        # Verify theme was created
        theme_path = temp_themes_dir / filename
        assert theme_path.exists()

        with open(theme_path) as f:
            data = json.load(f)
        assert data["metadata"]["name"] == "My Custom Theme"
        assert data["metadata"]["author"] == "Tester"

    def test_import_theme_from_bytes(self, service, temp_themes_dir):
        """Test importing a theme from bytes content (web mode)."""
        # Create theme data as bytes (simulating web upload)
        import_data = {
            "metadata": {"name": "Bytes Imported Theme"},
            "colors": {"light": {"accent": "#ABCDEF"}},
        }
        content_bytes = json.dumps(import_data).encode("utf-8")

        success, error = service.import_theme_from_bytes("bytes-theme.json", content_bytes)

        assert success is True
        assert error is None

        # Verify theme was imported
        themes = service.list_themes()
        names = [t.name for t in themes]
        assert "Bytes Imported Theme" in names

        # Verify the file content
        theme_path = temp_themes_dir / "bytes-theme.json"
        assert theme_path.exists()
        with open(theme_path) as f:
            data = json.load(f)
        assert data["metadata"]["name"] == "Bytes Imported Theme"

    def test_import_theme_from_bytes_invalid_json(self, service):
        """Test importing invalid JSON bytes."""
        invalid_bytes = b"not valid json"

        success, error = service.import_theme_from_bytes("invalid.json", invalid_bytes)

        assert success is False
        assert "invalid json" in error.lower()

    def test_import_theme_from_bytes_prevents_builtin_overwrite(self, service, temp_themes_dir):
        """Test that importing bytes cannot overwrite built-in themes."""
        # Try to import a theme with a built-in filename
        import_data = {
            "metadata": {"name": "Fake Default"},
            "colors": {"light": {"accent": "#000000"}},
        }
        content_bytes = json.dumps(import_data).encode("utf-8")

        success, error = service.import_theme_from_bytes("default.json", content_bytes)

        assert success is True  # Import should succeed
        assert error is None

        # But it should have been renamed to custom_default.json
        custom_path = temp_themes_dir / "custom_default.json"
        assert custom_path.exists()

        # Original default.json should still be the built-in
        success, theme, _ = service.load_theme("default.json")
        assert theme.metadata.name == "Default"  # Not "Fake Default"


class TestBuiltinThemes:
    """Tests for all built-in theme definitions."""

    @pytest.fixture
    def hex_pattern(self):
        """Regex pattern for valid hex color codes."""
        return re.compile(r"^#[0-9A-Fa-f]{6}$")

    @pytest.mark.parametrize("filename", list(ALL_BUILTIN_THEMES.keys()))
    def test_builtin_theme_has_valid_structure(self, filename):
        """Test all built-in themes have valid structure."""
        theme_data = ALL_BUILTIN_THEMES[filename]

        # Must have metadata
        assert "metadata" in theme_data
        assert "name" in theme_data["metadata"]
        assert "base" in theme_data["metadata"]
        assert theme_data["metadata"]["base"] in ("light", "dark")

        # Must have colors
        assert "colors" in theme_data
        assert "light" in theme_data["colors"]
        assert "dark" in theme_data["colors"]

    @pytest.mark.parametrize("filename", list(ALL_BUILTIN_THEMES.keys()))
    def test_builtin_theme_validates_with_schema(self, filename):
        """Test all built-in themes pass Pydantic validation."""
        theme_data = ALL_BUILTIN_THEMES[filename]
        # This should not raise
        theme = ThemeSchema.model_validate(theme_data)
        assert theme.metadata.name is not None

    @pytest.mark.parametrize("filename", list(ALL_BUILTIN_THEMES.keys()))
    def test_builtin_theme_has_all_light_colors(self, filename):
        """Test all built-in themes define all required light mode colors."""
        theme_data = ALL_BUILTIN_THEMES[filename]
        light_colors = theme_data["colors"]["light"]

        missing = []
        for token in REQUIRED_COLOR_TOKENS:
            if token not in light_colors or light_colors[token] is None:
                missing.append(token)

        assert not missing, f"{filename} light mode missing colors: {missing}"

    @pytest.mark.parametrize("filename", list(ALL_BUILTIN_THEMES.keys()))
    def test_builtin_theme_has_all_dark_colors(self, filename):
        """Test all built-in themes define all required dark mode colors."""
        theme_data = ALL_BUILTIN_THEMES[filename]
        dark_colors = theme_data["colors"]["dark"]

        missing = []
        for token in REQUIRED_COLOR_TOKENS:
            if token not in dark_colors or dark_colors[token] is None:
                missing.append(token)

        assert not missing, f"{filename} dark mode missing colors: {missing}"

    @pytest.mark.parametrize("filename", list(ALL_BUILTIN_THEMES.keys()))
    def test_builtin_theme_colors_are_valid_hex(self, filename, hex_pattern):
        """Test all color values are valid hex codes."""
        theme_data = ALL_BUILTIN_THEMES[filename]

        invalid_colors = []

        for mode in ["light", "dark"]:
            colors = theme_data["colors"][mode]
            for token, value in colors.items():
                if value is not None and not hex_pattern.match(value):
                    invalid_colors.append(f"{mode}.{token}: {value}")

        assert not invalid_colors, f"{filename} has invalid hex colors: {invalid_colors}"

    @pytest.mark.parametrize("filename", list(ALL_BUILTIN_THEMES.keys()))
    def test_builtin_theme_creates_color_classes(self, filename):
        """Test all built-in themes generate valid color classes."""
        theme_data = ALL_BUILTIN_THEMES[filename]
        theme = ThemeSchema.model_validate(theme_data)

        light, dark = create_colors_from_theme(theme)

        # Verify key attributes exist
        assert hasattr(light, "BG_PRIMARY")
        assert hasattr(light, "ACCENT")
        assert hasattr(light, "TEXT_PRIMARY")
        assert hasattr(dark, "BG_PRIMARY")
        assert hasattr(dark, "ACCENT")
        assert hasattr(dark, "TEXT_PRIMARY")

    def test_builtin_themes_frozenset_matches_definitions(self):
        """Test BUILTIN_THEMES frozenset matches ALL_BUILTIN_THEMES keys."""
        defined_themes = set(ALL_BUILTIN_THEMES.keys())
        registered_themes = set(BUILTIN_THEMES)

        # Check for themes defined but not registered
        unregistered = defined_themes - registered_themes
        assert not unregistered, f"Themes defined but not in BUILTIN_THEMES: {unregistered}"

        # Check for themes registered but not defined
        undefined = registered_themes - defined_themes
        assert not undefined, f"Themes in BUILTIN_THEMES but not defined: {undefined}"

    def test_all_expected_themes_present(self):
        """Test all expected popular themes are present."""
        expected_themes = {
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
        }

        actual_themes = set(ALL_BUILTIN_THEMES.keys())
        missing = expected_themes - actual_themes

        assert not missing, f"Missing expected themes: {missing}"
        assert len(actual_themes) == 14, f"Expected 14 themes, found {len(actual_themes)}"
