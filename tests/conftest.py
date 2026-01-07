"""Pytest fixtures for testing."""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.models.base import Base


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
        "gmail_thread_id": "thread_123",
        "subject": "Test Newsletter Issue #1",
        "sender_name": "Newsletter Bot",
        "sender_email": "newsletter@example.com",
        "received_at": datetime.now(timezone.utc),
        "snippet": "This is a test newsletter...",
        "body_text": "Full text content here",
        "body_html": "<p>Full HTML content here</p>",
        "size_bytes": 1024,
    }
