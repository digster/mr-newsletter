"""Unit tests for HomePage."""

import flet as ft
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


class TestHomePage:
    """Tests for HomePage view."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock app for testing."""
        mock = MagicMock()
        mock.page = MagicMock()
        mock.page.run_task = MagicMock()
        mock.page.update = MagicMock()
        mock.navigate = MagicMock()
        mock.show_snackbar = MagicMock()
        mock.gmail_service = MagicMock()
        mock.fetch_queue_service = AsyncMock()

        # Mock get_session context manager
        mock_session = AsyncMock()
        mock.get_session = MagicMock(return_value=mock_session)
        mock_session.__aenter__ = AsyncMock(return_value=MagicMock())
        mock_session.__aexit__ = AsyncMock(return_value=None)

        return mock

    def test_home_page_initialization(self, mock_app):
        """Test page initializes correctly."""
        with patch('src.ui.pages.home_page.NewsletterService'):
            from src.ui.pages.home_page import HomePage
            page = HomePage(app=mock_app)
            assert page is not None
            assert isinstance(page, ft.View)

    def test_home_page_route(self, mock_app):
        """Test page has correct route."""
        with patch('src.ui.pages.home_page.NewsletterService'):
            from src.ui.pages.home_page import HomePage
            page = HomePage(app=mock_app)
            assert page.route == "/home"

    def test_home_page_has_appbar(self, mock_app):
        """Test page has an AppBar."""
        with patch('src.ui.pages.home_page.NewsletterService'):
            from src.ui.pages.home_page import HomePage
            page = HomePage(app=mock_app)
            assert page.appbar is not None
            assert isinstance(page.appbar, ft.AppBar)

    def test_home_page_appbar_title(self, mock_app):
        """Test AppBar has correct title."""
        with patch('src.ui.pages.home_page.NewsletterService'):
            from src.ui.pages.home_page import HomePage
            page = HomePage(app=mock_app)
            assert page.appbar.title is not None
            assert isinstance(page.appbar.title, ft.Text)
            assert page.appbar.title.value == "Newsletter Manager"

    def test_home_page_appbar_has_actions(self, mock_app):
        """Test AppBar has action buttons."""
        with patch('src.ui.pages.home_page.NewsletterService'):
            from src.ui.pages.home_page import HomePage
            page = HomePage(app=mock_app)
            assert page.appbar.actions is not None
            assert len(page.appbar.actions) == 3  # Refresh, Manage, Settings

    def test_home_page_has_grid_view(self, mock_app):
        """Test page has a GridView for newsletters."""
        with patch('src.ui.pages.home_page.NewsletterService'):
            from src.ui.pages.home_page import HomePage
            page = HomePage(app=mock_app)
            assert page.newsletters_grid is not None
            assert isinstance(page.newsletters_grid, ft.GridView)

    def test_home_page_grid_has_three_columns(self, mock_app):
        """Test GridView has 3 columns."""
        with patch('src.ui.pages.home_page.NewsletterService'):
            from src.ui.pages.home_page import HomePage
            page = HomePage(app=mock_app)
            assert page.newsletters_grid.runs_count == 3

    def test_home_page_has_loading_indicator(self, mock_app):
        """Test page has a loading ProgressRing."""
        with patch('src.ui.pages.home_page.NewsletterService'):
            from src.ui.pages.home_page import HomePage
            page = HomePage(app=mock_app)
            assert page.loading is not None
            assert isinstance(page.loading, ft.ProgressRing)

    def test_home_page_has_empty_state(self, mock_app):
        """Test page has empty state column."""
        with patch('src.ui.pages.home_page.NewsletterService'):
            from src.ui.pages.home_page import HomePage
            page = HomePage(app=mock_app)
            assert page.empty_state is not None
            assert isinstance(page.empty_state, ft.Column)

    def test_home_page_triggers_load_on_init(self, mock_app):
        """Test page triggers _load_newsletters on initialization."""
        with patch('src.ui.pages.home_page.NewsletterService'):
            from src.ui.pages.home_page import HomePage
            page = HomePage(app=mock_app)
            mock_app.page.run_task.assert_called()

    def test_home_page_has_controls(self, mock_app):
        """Test page has controls."""
        with patch('src.ui.pages.home_page.NewsletterService'):
            from src.ui.pages.home_page import HomePage
            page = HomePage(app=mock_app)
            assert page.controls is not None
            assert len(page.controls) > 0
