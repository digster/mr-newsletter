"""Pytest fixtures for testing."""

import asyncio
from typing import AsyncGenerator
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.models.base import Base
from tests.fixtures.sample_data import (
    create_email,
    create_gmail_label,
    create_newsletter,
    create_sample_emails,
    create_sample_gmail_labels,
    create_sample_newsletters,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def async_engine():
    """Create async engine for tests using SQLite."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    await engine.dispose()


@pytest_asyncio.fixture
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create async session for tests."""
    async_session_maker = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()


@pytest.fixture
def sample_newsletter_data():
    """Sample newsletter data for testing."""
    return {
        "name": "Tech Weekly",
        "gmail_label_id": "Label_123",
        "gmail_label_name": "Newsletters/Tech",
        "description": "Weekly tech news digest",
        "auto_fetch_enabled": True,
        "fetch_interval_minutes": 1440,
    }


@pytest.fixture
def sample_email_data():
    """Sample email data for testing."""
    from datetime import datetime, timezone

    return {
        "gmail_message_id": "msg_123456",
        "subject": "Test Newsletter Issue #1",
        "sender_name": "Newsletter Bot",
        "sender_email": "newsletter@example.com",
        "received_at": datetime.now(timezone.utc),
        "snippet": "This is a test newsletter...",
        "body_text": "Full text content here",
        "body_html": "<p>Full HTML content here</p>",
        "size_bytes": 1024,
    }


# ============================================================================
# Model Fixtures
# ============================================================================


@pytest.fixture
def sample_newsletter():
    """Create a single sample Newsletter instance."""
    return create_newsletter()


@pytest.fixture
def sample_newsletters():
    """Create a list of sample Newsletter instances."""
    return create_sample_newsletters(count=3)


@pytest.fixture
def sample_email():
    """Create a single sample Email instance."""
    return create_email()


@pytest.fixture
def sample_emails():
    """Create a list of sample Email instances."""
    return create_sample_emails(newsletter_id=1, count=5)


@pytest.fixture
def sample_gmail_labels():
    """Create a list of sample GmailLabel instances."""
    return create_sample_gmail_labels(count=5)


# ============================================================================
# Mock Service Fixtures
# ============================================================================


@pytest.fixture
def mock_gmail_service(sample_gmail_labels):
    """Mock GmailService for testing without API calls."""
    mock = MagicMock()
    mock.get_user_email.return_value = "test@gmail.com"
    mock.get_labels.return_value = sample_gmail_labels
    mock.get_messages_by_label.return_value = (["msg_1", "msg_2", "msg_3"], None)
    mock.get_message_detail.return_value = None
    mock.get_message_count_for_label.return_value = 25
    return mock


@pytest.fixture
def mock_auth_service():
    """Mock AuthService for testing."""
    mock = AsyncMock()
    mock.is_app_configured = AsyncMock(return_value=True)
    mock.get_user_credentials = AsyncMock(
        return_value=MagicMock(
            success=True,
            credentials=MagicMock(),
            user_email="test@gmail.com",
        )
    )
    mock.get_current_user_email = AsyncMock(return_value="test@gmail.com")
    mock.save_app_credentials = AsyncMock(return_value=True)
    mock.logout = AsyncMock(return_value=True)
    mock.clear_all_credentials = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_newsletter_service(sample_newsletters, sample_newsletter):
    """Mock NewsletterService for testing."""
    mock = AsyncMock()
    mock.get_all = AsyncMock(return_value=sample_newsletters)
    mock.get_by_id = AsyncMock(return_value=sample_newsletter)
    mock.create = AsyncMock(return_value=sample_newsletter)
    mock.update = AsyncMock(return_value=sample_newsletter)
    mock.delete = AsyncMock(return_value=True)
    mock.update_counts = AsyncMock(return_value=sample_newsletter)
    return mock


@pytest.fixture
def mock_email_service(sample_emails, sample_email):
    """Mock EmailService for testing."""
    mock = AsyncMock()
    mock.get_by_newsletter = AsyncMock(return_value=sample_emails)
    mock.get_by_id = AsyncMock(return_value=sample_email)
    mock.mark_as_read = AsyncMock(return_value=sample_email)
    mock.mark_as_unread = AsyncMock(return_value=sample_email)
    mock.toggle_star = AsyncMock(return_value=sample_email)
    mock.archive = AsyncMock(return_value=sample_email)
    mock.delete = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_fetch_queue_service():
    """Mock FetchQueueService for testing."""
    mock = AsyncMock()
    mock.queue_fetch = AsyncMock(return_value=None)
    mock.queue_all_newsletters = AsyncMock(return_value=3)
    mock.get_queue_status = AsyncMock(return_value={"pending": 0, "processing": 0})
    return mock


# ============================================================================
# UI Mock Fixtures
# ============================================================================


@pytest.fixture
def mock_flet_page():
    """Mock Flet Page object for unit testing UI components."""
    import flet as ft

    mock_page = MagicMock()
    mock_page.route = "/home"
    mock_page.theme_mode = ft.ThemeMode.SYSTEM
    mock_page.views = []
    mock_page.update = MagicMock()
    mock_page.go = MagicMock()
    mock_page.run_task = MagicMock()
    mock_page.open = MagicMock()
    mock_page.close = MagicMock()
    mock_page.snack_bar = None
    mock_page.width = 1200
    mock_page.height = 800
    mock_page.window = MagicMock()
    mock_page.window.width = 1200
    mock_page.window.height = 800
    mock_page.client_storage = MagicMock()
    mock_page.client_storage.get = MagicMock(return_value=None)
    mock_page.client_storage.set = MagicMock()
    return mock_page


@pytest.fixture
def mock_router(mock_flet_page):
    """Mock Router for navigation testing."""
    mock = MagicMock()
    mock.page = mock_flet_page
    mock.go_home = MagicMock()
    mock.go_login = MagicMock()
    mock.go_setup = MagicMock()
    mock.go_newsletters = MagicMock()
    mock.go_newsletter = MagicMock()
    mock.go_email = MagicMock()
    mock.go_settings = MagicMock()
    mock.go_back = MagicMock()
    return mock


@pytest.fixture
def mock_app(
    mock_flet_page,
    mock_router,
    mock_gmail_service,
    mock_auth_service,
    mock_newsletter_service,
    mock_email_service,
    mock_fetch_queue_service,
    async_session,
):
    """Mock NewsletterApp for comprehensive UI testing."""
    mock = MagicMock()
    mock.page = mock_flet_page
    mock.router = mock_router
    mock.gmail_service = mock_gmail_service
    mock.auth_service = mock_auth_service
    mock.newsletter_service = mock_newsletter_service
    mock.email_service = mock_email_service
    mock.fetch_queue_service = mock_fetch_queue_service
    mock.show_snackbar = MagicMock()
    mock.navigate = MagicMock()

    # Mock session context manager
    async def mock_get_session():
        return async_session

    mock.get_session = mock_get_session
    return mock
