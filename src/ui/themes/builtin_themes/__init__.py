"""Built-in theme definitions.

This module contains all built-in themes for the Newsletter Reader application.
Each theme is defined in its own file and exported here for use by ThemeService.
"""

from .catppuccin import CATPPUCCIN_LATTE_THEME, CATPPUCCIN_MOCHA_THEME
from .dark_slate import DARK_SLATE_THEME
from .default import DEFAULT_THEME
from .dracula import DRACULA_THEME
from .gruvbox import GRUVBOX_DARK_THEME, GRUVBOX_LIGHT_THEME
from .light_clean import LIGHT_CLEAN_THEME
from .midnight import MIDNIGHT_THEME
from .nord import NORD_THEME
from .one_dark import ONE_DARK_THEME
from .solarized import SOLARIZED_DARK_THEME, SOLARIZED_LIGHT_THEME
from .tokyo_night import TOKYO_NIGHT_THEME

# Mapping of filename to theme data dictionary
# This is used by ThemeService to create theme files
ALL_BUILTIN_THEMES: dict[str, dict] = {
    # Original themes
    "default.json": DEFAULT_THEME,
    "dark-slate.json": DARK_SLATE_THEME,
    "light-clean.json": LIGHT_CLEAN_THEME,
    "midnight.json": MIDNIGHT_THEME,
    # Popular color schemes
    "nord.json": NORD_THEME,
    "solarized-light.json": SOLARIZED_LIGHT_THEME,
    "solarized-dark.json": SOLARIZED_DARK_THEME,
    "dracula.json": DRACULA_THEME,
    "gruvbox-light.json": GRUVBOX_LIGHT_THEME,
    "gruvbox-dark.json": GRUVBOX_DARK_THEME,
    "catppuccin-latte.json": CATPPUCCIN_LATTE_THEME,
    "catppuccin-mocha.json": CATPPUCCIN_MOCHA_THEME,
    "one-dark.json": ONE_DARK_THEME,
    "tokyo-night.json": TOKYO_NIGHT_THEME,
}

__all__ = [
    "ALL_BUILTIN_THEMES",
    "DEFAULT_THEME",
    "DARK_SLATE_THEME",
    "LIGHT_CLEAN_THEME",
    "MIDNIGHT_THEME",
    "NORD_THEME",
    "SOLARIZED_LIGHT_THEME",
    "SOLARIZED_DARK_THEME",
    "DRACULA_THEME",
    "GRUVBOX_LIGHT_THEME",
    "GRUVBOX_DARK_THEME",
    "CATPPUCCIN_LATTE_THEME",
    "CATPPUCCIN_MOCHA_THEME",
    "ONE_DARK_THEME",
    "TOKYO_NIGHT_THEME",
]
