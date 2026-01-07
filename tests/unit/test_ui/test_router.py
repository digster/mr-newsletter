"""Unit tests for Router."""

import pytest
from unittest.mock import MagicMock, patch

from src.ui.router import Router


class TestRouter:
    """Tests for Router class."""

    @pytest.fixture
    def mock_app(self):
        """Create a mock app for testing."""
        mock = MagicMock()
        mock.navigate = MagicMock()
        mock.page = MagicMock()
        mock.page.views = [MagicMock(route="/home"), MagicMock(route="/settings")]
        mock.page.go = MagicMock()
        return mock

    @pytest.fixture
    def router(self, mock_app):
        """Create a Router instance with mock app."""
        return Router(app=mock_app)

    def test_router_initialization(self, mock_app):
        """Test router initializes with app reference."""
        router = Router(app=mock_app)
        assert router.app == mock_app

    def test_router_navigate(self, router, mock_app):
        """Test navigate calls app.navigate."""
        router.navigate("/test")
        mock_app.navigate.assert_called_once_with("/test")

    def test_router_go_home(self, router, mock_app):
        """Test go_home navigates to /home."""
        router.go_home()
        mock_app.navigate.assert_called_once_with("/home")

    def test_router_go_login(self, router, mock_app):
        """Test go_login navigates to /login."""
        router.go_login()
        mock_app.navigate.assert_called_once_with("/login")

    def test_router_go_setup(self, router, mock_app):
        """Test go_setup navigates to /setup."""
        router.go_setup()
        mock_app.navigate.assert_called_once_with("/setup")

    def test_router_go_newsletters(self, router, mock_app):
        """Test go_newsletters navigates to /newsletters."""
        router.go_newsletters()
        mock_app.navigate.assert_called_once_with("/newsletters")

    def test_router_go_newsletter_with_id(self, router, mock_app):
        """Test go_newsletter navigates to /newsletter/{id}."""
        router.go_newsletter(42)
        mock_app.navigate.assert_called_once_with("/newsletter/42")

    def test_router_go_email_with_id(self, router, mock_app):
        """Test go_email navigates to /email/{id}."""
        router.go_email(123)
        mock_app.navigate.assert_called_once_with("/email/123")

    def test_router_go_settings(self, router, mock_app):
        """Test go_settings navigates to /settings."""
        router.go_settings()
        mock_app.navigate.assert_called_once_with("/settings")

    def test_router_go_back_pops_view(self, router, mock_app):
        """Test go_back pops view from stack."""
        initial_view_count = len(mock_app.page.views)
        router.go_back()
        assert len(mock_app.page.views) == initial_view_count - 1

    def test_router_go_back_navigates_to_top_view(self, router, mock_app):
        """Test go_back navigates to the new top view's route."""
        router.go_back()
        mock_app.page.go.assert_called_once_with("/home")

    def test_router_go_back_with_single_view(self, mock_app):
        """Test go_back with only one view doesn't navigate."""
        mock_app.page.views = [MagicMock(route="/home")]
        router = Router(app=mock_app)
        router.go_back()
        # After popping, views is empty, so go shouldn't be called
        mock_app.page.go.assert_not_called()

    def test_router_go_newsletter_with_different_ids(self, router, mock_app):
        """Test go_newsletter works with various IDs."""
        test_ids = [1, 100, 999, 0]
        for test_id in test_ids:
            mock_app.navigate.reset_mock()
            router.go_newsletter(test_id)
            mock_app.navigate.assert_called_once_with(f"/newsletter/{test_id}")

    def test_router_go_email_with_different_ids(self, router, mock_app):
        """Test go_email works with various IDs."""
        test_ids = [1, 100, 999, 0]
        for test_id in test_ids:
            mock_app.navigate.reset_mock()
            router.go_email(test_id)
            mock_app.navigate.assert_called_once_with(f"/email/{test_id}")
