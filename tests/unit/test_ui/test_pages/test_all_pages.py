"""Unit tests for all page views - basic structure tests."""

import flet as ft
import pytest
from unittest.mock import MagicMock, AsyncMock, patch


@pytest.fixture
def mock_app():
    """Create a comprehensive mock app for page testing."""
    mock = MagicMock()
    mock.page = MagicMock()
    mock.page.run_task = MagicMock()
    mock.page.update = MagicMock()
    mock.page.views = []
    mock.page.go = MagicMock()
    mock.navigate = MagicMock()
    mock.show_snackbar = MagicMock()
    mock.gmail_service = MagicMock()
    mock.gmail_service.get_labels = MagicMock(return_value=[])
    mock.fetch_queue_service = AsyncMock()
    mock.auth_service = AsyncMock()

    # Mock get_session context manager
    mock_session = MagicMock()
    mock_session.__aenter__ = AsyncMock(return_value=MagicMock())
    mock_session.__aexit__ = AsyncMock(return_value=None)

    async def get_session():
        return mock_session

    mock.get_session = get_session
    return mock


class TestSetupPage:
    """Tests for SetupPage view."""

    def test_setup_page_initialization(self, mock_app):
        """Test page initializes correctly."""
        from src.ui.pages.setup_page import SetupPage
        page = SetupPage(app=mock_app)
        assert page is not None
        assert isinstance(page, ft.View)

    def test_setup_page_route(self, mock_app):
        """Test page has correct route."""
        from src.ui.pages.setup_page import SetupPage
        page = SetupPage(app=mock_app)
        assert page.route == "/setup"

    def test_setup_page_has_no_appbar(self, mock_app):
        """Test setup page has no AppBar (standalone setup flow)."""
        from src.ui.pages.setup_page import SetupPage
        page = SetupPage(app=mock_app)
        assert page.appbar is None

    def test_setup_page_has_client_id_field(self, mock_app):
        """Test page has client ID field."""
        from src.ui.pages.setup_page import SetupPage
        page = SetupPage(app=mock_app)
        assert page.client_id_field is not None
        assert isinstance(page.client_id_field, ft.TextField)

    def test_setup_page_has_client_secret_field(self, mock_app):
        """Test page has client secret field."""
        from src.ui.pages.setup_page import SetupPage
        page = SetupPage(app=mock_app)
        assert page.client_secret_field is not None
        assert isinstance(page.client_secret_field, ft.TextField)
        assert page.client_secret_field.password is True


class TestLoginPage:
    """Tests for LoginPage view."""

    def test_login_page_initialization(self, mock_app):
        """Test page initializes correctly."""
        from src.ui.pages.login_page import LoginPage
        page = LoginPage(app=mock_app)
        assert page is not None
        assert isinstance(page, ft.View)

    def test_login_page_route(self, mock_app):
        """Test page has correct route."""
        from src.ui.pages.login_page import LoginPage
        page = LoginPage(app=mock_app)
        assert page.route == "/login"

    def test_login_page_has_controls(self, mock_app):
        """Test page has controls."""
        from src.ui.pages.login_page import LoginPage
        page = LoginPage(app=mock_app)
        assert page.controls is not None
        assert len(page.controls) > 0

    def test_login_page_has_loading_indicator(self, mock_app):
        """Test page has loading indicator."""
        from src.ui.pages.login_page import LoginPage
        page = LoginPage(app=mock_app)
        assert page.loading is not None
        assert isinstance(page.loading, ft.ProgressRing)


class TestNewslettersPage:
    """Tests for NewslettersPage view."""

    def test_newsletters_page_initialization(self, mock_app):
        """Test page initializes correctly."""
        with patch('src.ui.pages.newsletters_page.NewsletterService'):
            from src.ui.pages.newsletters_page import NewslettersPage
            page = NewslettersPage(app=mock_app)
            assert page is not None
            assert isinstance(page, ft.View)

    def test_newsletters_page_route(self, mock_app):
        """Test page has correct route."""
        with patch('src.ui.pages.newsletters_page.NewsletterService'):
            from src.ui.pages.newsletters_page import NewslettersPage
            page = NewslettersPage(app=mock_app)
            assert page.route == "/newsletters"

    def test_newsletters_page_has_appbar(self, mock_app):
        """Test page has an AppBar."""
        with patch('src.ui.pages.newsletters_page.NewsletterService'):
            from src.ui.pages.newsletters_page import NewslettersPage
            page = NewslettersPage(app=mock_app)
            assert page.appbar is not None

    def test_newsletters_page_has_list_view(self, mock_app):
        """Test page has a ListView for newsletters."""
        with patch('src.ui.pages.newsletters_page.NewsletterService'):
            from src.ui.pages.newsletters_page import NewslettersPage
            page = NewslettersPage(app=mock_app)
            assert page.newsletters_list is not None
            assert isinstance(page.newsletters_list, ft.ListView)


class TestEmailListPage:
    """Tests for EmailListPage view."""

    def test_email_list_page_initialization(self, mock_app):
        """Test page initializes correctly."""
        with patch('src.ui.pages.email_list_page.NewsletterService'), \
             patch('src.ui.pages.email_list_page.EmailService'):
            from src.ui.pages.email_list_page import EmailListPage
            page = EmailListPage(app=mock_app, newsletter_id=1)
            assert page is not None
            assert isinstance(page, ft.View)

    def test_email_list_page_route_includes_id(self, mock_app):
        """Test page route includes newsletter ID."""
        with patch('src.ui.pages.email_list_page.NewsletterService'), \
             patch('src.ui.pages.email_list_page.EmailService'):
            from src.ui.pages.email_list_page import EmailListPage
            page = EmailListPage(app=mock_app, newsletter_id=42)
            assert page.route == "/newsletter/42"

    def test_email_list_page_stores_newsletter_id(self, mock_app):
        """Test page stores newsletter ID."""
        with patch('src.ui.pages.email_list_page.NewsletterService'), \
             patch('src.ui.pages.email_list_page.EmailService'):
            from src.ui.pages.email_list_page import EmailListPage
            page = EmailListPage(app=mock_app, newsletter_id=42)
            assert page.newsletter_id == 42

    def test_email_list_page_has_list_view(self, mock_app):
        """Test page has a ListView for emails."""
        with patch('src.ui.pages.email_list_page.NewsletterService'), \
             patch('src.ui.pages.email_list_page.EmailService'):
            from src.ui.pages.email_list_page import EmailListPage
            page = EmailListPage(app=mock_app, newsletter_id=1)
            assert page.emails_list is not None
            assert isinstance(page.emails_list, ft.ListView)


class TestEmailReaderPage:
    """Tests for EmailReaderPage view."""

    def test_email_reader_page_initialization(self, mock_app):
        """Test page initializes correctly."""
        with patch('src.ui.pages.email_reader_page.EmailService'):
            from src.ui.pages.email_reader_page import EmailReaderPage
            page = EmailReaderPage(app=mock_app, email_id=1)
            assert page is not None
            assert isinstance(page, ft.View)

    def test_email_reader_page_route_includes_id(self, mock_app):
        """Test page route includes email ID."""
        with patch('src.ui.pages.email_reader_page.EmailService'):
            from src.ui.pages.email_reader_page import EmailReaderPage
            page = EmailReaderPage(app=mock_app, email_id=99)
            assert page.route == "/email/99"

    def test_email_reader_page_stores_email_id(self, mock_app):
        """Test page stores email ID."""
        with patch('src.ui.pages.email_reader_page.EmailService'):
            from src.ui.pages.email_reader_page import EmailReaderPage
            page = EmailReaderPage(app=mock_app, email_id=99)
            assert page.email_id == 99

    def test_email_reader_page_has_appbar(self, mock_app):
        """Test page has an AppBar."""
        with patch('src.ui.pages.email_reader_page.EmailService'):
            from src.ui.pages.email_reader_page import EmailReaderPage
            page = EmailReaderPage(app=mock_app, email_id=1)
            assert page.appbar is not None


class TestSettingsPage:
    """Tests for SettingsPage view."""

    def test_settings_page_initialization(self, mock_app):
        """Test page initializes correctly."""
        from src.ui.pages.settings_page import SettingsPage
        page = SettingsPage(app=mock_app)
        assert page is not None
        assert isinstance(page, ft.View)

    def test_settings_page_route(self, mock_app):
        """Test page has correct route."""
        from src.ui.pages.settings_page import SettingsPage
        page = SettingsPage(app=mock_app)
        assert page.route == "/settings"

    def test_settings_page_has_appbar(self, mock_app):
        """Test page has an AppBar."""
        from src.ui.pages.settings_page import SettingsPage
        page = SettingsPage(app=mock_app)
        assert page.appbar is not None

    def test_settings_page_has_theme_dropdown(self, mock_app):
        """Test page has theme dropdown."""
        from src.ui.pages.settings_page import SettingsPage
        page = SettingsPage(app=mock_app)
        assert page.theme_dropdown is not None
        assert isinstance(page.theme_dropdown, ft.Dropdown)

    def test_settings_page_theme_dropdown_has_options(self, mock_app):
        """Test theme dropdown has System, Light, Dark options."""
        from src.ui.pages.settings_page import SettingsPage
        page = SettingsPage(app=mock_app)
        options = page.theme_dropdown.options
        assert len(options) == 3
