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

    def test_home_page_has_sidebar(self, mock_app):
        """Test page has a sidebar for navigation."""
        with patch('src.ui.pages.home_page.NewsletterService'):
            from src.ui.pages.home_page import HomePage
            page = HomePage(app=mock_app)
            assert page.sidebar is not None

    def test_home_page_has_grid_view(self, mock_app):
        """Test page has a GridView for newsletters."""
        with patch('src.ui.pages.home_page.NewsletterService'):
            from src.ui.pages.home_page import HomePage
            page = HomePage(app=mock_app)
            assert page.newsletters_grid is not None
            assert isinstance(page.newsletters_grid, ft.GridView)

    def test_home_page_grid_has_columns(self, mock_app):
        """Test GridView has columns configured."""
        with patch('src.ui.pages.home_page.NewsletterService'):
            from src.ui.pages.home_page import HomePage
            page = HomePage(app=mock_app)
            assert page.newsletters_grid.runs_count is not None

    def test_home_page_has_loading_indicator(self, mock_app):
        """Test page has a loading ProgressRing."""
        with patch('src.ui.pages.home_page.NewsletterService'):
            from src.ui.pages.home_page import HomePage
            page = HomePage(app=mock_app)
            assert page.loading is not None
            assert isinstance(page.loading, ft.ProgressRing)

    def test_home_page_has_empty_state(self, mock_app):
        """Test page has empty state container."""
        with patch('src.ui.pages.home_page.NewsletterService'):
            from src.ui.pages.home_page import HomePage
            page = HomePage(app=mock_app)
            assert page.empty_state is not None
            # Empty state is now wrapped in a Container
            assert isinstance(page.empty_state, ft.Container)

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
