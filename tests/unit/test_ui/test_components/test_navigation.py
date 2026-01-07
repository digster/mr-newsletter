"""Unit tests for Navigation component."""

import flet as ft
import pytest
from unittest.mock import MagicMock

from src.ui.components.navigation import Navigation


class TestNavigation:
    """Tests for NavigationRail component."""

    def test_navigation_creates_successfully(self):
        """Test navigation component can be instantiated."""
        nav = Navigation()
        assert nav is not None
        assert isinstance(nav, ft.NavigationRail)

    def test_navigation_has_three_destinations(self):
        """Test navigation has Home, Newsletters, Settings destinations."""
        nav = Navigation()
        assert len(nav.destinations) == 3

    def test_navigation_default_selected_index_is_zero(self):
        """Test default selection is index 0 (Home)."""
        nav = Navigation()
        assert nav.selected_index == 0

    def test_navigation_label_type_is_all(self):
        """Test labels are always visible."""
        nav = Navigation()
        assert nav.label_type == ft.NavigationRailLabelType.ALL

    def test_navigation_home_destination(self):
        """Test Home destination configuration."""
        nav = Navigation()
        home_dest = nav.destinations[0]
        assert home_dest.label == "Home"
        assert home_dest.icon == ft.Icons.HOME_OUTLINED
        assert home_dest.selected_icon == ft.Icons.HOME

    def test_navigation_newsletters_destination(self):
        """Test Newsletters destination configuration."""
        nav = Navigation()
        newsletters_dest = nav.destinations[1]
        assert newsletters_dest.label == "Newsletters"
        assert newsletters_dest.icon == ft.Icons.FOLDER_OUTLINED
        assert newsletters_dest.selected_icon == ft.Icons.FOLDER

    def test_navigation_settings_destination(self):
        """Test Settings destination configuration."""
        nav = Navigation()
        settings_dest = nav.destinations[2]
        assert settings_dest.label == "Settings"
        assert settings_dest.icon == ft.Icons.SETTINGS_OUTLINED
        assert settings_dest.selected_icon == ft.Icons.SETTINGS

    def test_navigation_on_change_callback_is_set(self):
        """Test on_change callback is set when provided."""
        callback = MagicMock()
        nav = Navigation(on_change=callback)
        assert nav.on_change == callback

    def test_navigation_on_change_callback_none_by_default(self):
        """Test on_change callback is None when not provided."""
        nav = Navigation()
        assert nav.on_change is None

    def test_navigation_icons_are_set(self):
        """Test all icons are set."""
        nav = Navigation()
        for dest in nav.destinations:
            assert dest.icon is not None
            assert dest.selected_icon is not None

    def test_navigation_destinations_have_labels(self):
        """Test all destinations have non-empty labels."""
        nav = Navigation()
        for dest in nav.destinations:
            assert dest.label is not None
            assert len(dest.label) > 0
