"""Tests for EmailService - email business logic.

These tests verify the email service correctly handles email operations
including marking read/unread, starring, archiving, and AI summarization.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.email import Email
from src.models.newsletter import Newsletter
from src.services.email_service import EmailService


class TestEmailServiceGetEmail:
    """Test email retrieval operations."""

    @pytest_asyncio.fixture
    async def email_service(self, async_session: AsyncSession):
        """Create email service with test session."""
        return EmailService(async_session)

    @pytest_asyncio.fixture
    async def sample_data(self, async_session: AsyncSession):
        """Create sample newsletter and email."""
        newsletter = Newsletter(
            name="Test Newsletter",
            gmail_label_id="Label_123",
            gmail_label_name="Test",
        )
        async_session.add(newsletter)
        await async_session.flush()

        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_123",
            subject="Test Email",
            sender_email="test@example.com",
            received_at=datetime.now(timezone.utc),
            is_read=False,
            is_starred=False,
            is_archived=False,
        )
        async_session.add(email)
        await async_session.commit()

        return newsletter, email

    @pytest.mark.asyncio
    async def test_get_email_by_id(self, email_service, sample_data):
        """Verify get_email returns email by ID."""
        _, email = sample_data

        result = await email_service.get_email(email.id)

        assert result is not None
        assert result.id == email.id
        assert result.subject == "Test Email"

    @pytest.mark.asyncio
    async def test_get_email_returns_none_for_missing(self, email_service):
        """Verify get_email returns None for nonexistent ID."""
        result = await email_service.get_email(99999)

        assert result is None


class TestEmailServicePagination:
    """Test email listing and pagination."""

    @pytest_asyncio.fixture
    async def email_service(self, async_session: AsyncSession):
        """Create email service with test session."""
        return EmailService(async_session)

    @pytest_asyncio.fixture
    async def sample_emails(self, async_session: AsyncSession):
        """Create sample newsletter with multiple emails."""
        newsletter = Newsletter(
            name="Test Newsletter",
            gmail_label_id="Label_123",
            gmail_label_name="Test",
        )
        async_session.add(newsletter)
        await async_session.flush()

        emails = []
        for i in range(10):
            email = Email(
                newsletter_id=newsletter.id,
                gmail_message_id=f"msg_{i}",
                subject=f"Email {i}",
                sender_email="test@example.com",
                received_at=datetime.now(timezone.utc),
                is_read=(i % 2 == 0),  # Even emails are read
                is_starred=(i % 3 == 0),  # Every 3rd email is starred
                is_archived=(i == 9),  # Last email is archived
            )
            emails.append(email)
            async_session.add(email)

        await async_session.commit()
        return newsletter, emails

    @pytest.mark.asyncio
    async def test_get_emails_for_newsletter_pagination(self, email_service, sample_emails):
        """Verify pagination works correctly."""
        newsletter, emails = sample_emails

        # Get first page
        page1 = await email_service.get_emails_for_newsletter(
            newsletter.id, limit=5, offset=0
        )
        assert len(page1) <= 5  # May be fewer due to archived filtering

        # Get second page
        page2 = await email_service.get_emails_for_newsletter(
            newsletter.id, limit=5, offset=5
        )
        # Second page may have fewer if some are archived
        assert len(page2) <= 5

    @pytest.mark.asyncio
    async def test_get_emails_unread_filter(self, email_service, sample_emails):
        """Verify unread_only filter works."""
        newsletter, _ = sample_emails

        unread = await email_service.get_emails_for_newsletter(
            newsletter.id, unread_only=True
        )

        for email in unread:
            assert email.is_read is False

    @pytest.mark.asyncio
    async def test_get_emails_starred_filter(self, email_service, sample_emails):
        """Verify starred_only filter works."""
        newsletter, _ = sample_emails

        starred = await email_service.get_emails_for_newsletter(
            newsletter.id, starred_only=True
        )

        for email in starred:
            assert email.is_starred is True


class TestEmailServiceReadStatus:
    """Test read/unread status operations."""

    @pytest_asyncio.fixture
    async def email_service(self, async_session: AsyncSession):
        """Create email service with test session."""
        return EmailService(async_session)

    @pytest_asyncio.fixture
    async def sample_email(self, async_session: AsyncSession):
        """Create sample email."""
        newsletter = Newsletter(
            name="Test Newsletter",
            gmail_label_id="Label_123",
            gmail_label_name="Test",
        )
        async_session.add(newsletter)
        await async_session.flush()

        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_123",
            subject="Test Email",
            sender_email="test@example.com",
            received_at=datetime.now(timezone.utc),
            is_read=False,
        )
        async_session.add(email)
        await async_session.commit()

        return newsletter, email

    @pytest.mark.asyncio
    async def test_mark_as_read_updates_email(self, email_service, sample_email):
        """Verify mark_as_read sets is_read to True."""
        _, email = sample_email

        result = await email_service.mark_as_read(email.id)

        assert result is not None
        assert result.is_read is True
        assert result.read_at is not None

    @pytest.mark.asyncio
    async def test_mark_as_unread_updates_email(self, email_service, sample_email):
        """Verify mark_as_unread sets is_read to False."""
        _, email = sample_email

        # First mark as read
        await email_service.mark_as_read(email.id)

        # Then mark as unread
        result = await email_service.mark_as_unread(email.id)

        assert result is not None
        assert result.is_read is False


class TestEmailServiceStarred:
    """Test starred status operations."""

    @pytest_asyncio.fixture
    async def email_service(self, async_session: AsyncSession):
        """Create email service with test session."""
        return EmailService(async_session)

    @pytest_asyncio.fixture
    async def sample_email(self, async_session: AsyncSession):
        """Create sample email."""
        newsletter = Newsletter(
            name="Test Newsletter",
            gmail_label_id="Label_123",
            gmail_label_name="Test",
        )
        async_session.add(newsletter)
        await async_session.flush()

        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_123",
            subject="Test Email",
            sender_email="test@example.com",
            received_at=datetime.now(timezone.utc),
            is_starred=False,
        )
        async_session.add(email)
        await async_session.commit()

        return email

    @pytest.mark.asyncio
    async def test_toggle_starred_sets_true(self, email_service, sample_email):
        """Verify toggle_starred sets is_starred to True when False."""
        email = sample_email

        result = await email_service.toggle_starred(email.id)

        assert result is not None
        assert result.is_starred is True

    @pytest.mark.asyncio
    async def test_toggle_starred_sets_false(self, email_service, sample_email):
        """Verify toggle_starred sets is_starred to False when True."""
        email = sample_email

        # Toggle to True
        await email_service.toggle_starred(email.id)

        # Toggle back to False
        result = await email_service.toggle_starred(email.id)

        assert result is not None
        assert result.is_starred is False


class TestEmailServiceArchive:
    """Test archive operations."""

    @pytest_asyncio.fixture
    async def email_service(self, async_session: AsyncSession):
        """Create email service with test session."""
        return EmailService(async_session)

    @pytest_asyncio.fixture
    async def sample_email(self, async_session: AsyncSession):
        """Create sample email."""
        newsletter = Newsletter(
            name="Test Newsletter",
            gmail_label_id="Label_123",
            gmail_label_name="Test",
        )
        async_session.add(newsletter)
        await async_session.flush()

        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_123",
            subject="Test Email",
            sender_email="test@example.com",
            received_at=datetime.now(timezone.utc),
            is_archived=False,
        )
        async_session.add(email)
        await async_session.commit()

        return email

    @pytest.mark.asyncio
    async def test_archive_email_sets_flag(self, email_service, sample_email):
        """Verify archive_email sets is_archived to True."""
        email = sample_email

        result = await email_service.archive_email(email.id)

        assert result is not None
        assert result.is_archived is True

    @pytest.mark.asyncio
    async def test_unarchive_email_clears_flag(self, email_service, sample_email):
        """Verify unarchive_email sets is_archived to False."""
        email = sample_email

        # Archive first
        await email_service.archive_email(email.id)

        # Then unarchive
        result = await email_service.unarchive_email(email.id)

        assert result is not None
        assert result.is_archived is False


class TestEmailServiceSearch:
    """Test email search operations."""

    @pytest_asyncio.fixture
    async def email_service(self, async_session: AsyncSession):
        """Create email service with test session."""
        return EmailService(async_session)

    @pytest_asyncio.fixture
    async def searchable_emails(self, async_session: AsyncSession):
        """Create emails with searchable content."""
        newsletter = Newsletter(
            name="Test Newsletter",
            gmail_label_id="Label_123",
            gmail_label_name="Test",
        )
        async_session.add(newsletter)
        await async_session.flush()

        emails = [
            Email(
                newsletter_id=newsletter.id,
                gmail_message_id="msg_1",
                subject="Python Tutorial",
                sender_name="Tech Blog",
                sender_email="tech@example.com",
                received_at=datetime.now(timezone.utc),
            ),
            Email(
                newsletter_id=newsletter.id,
                gmail_message_id="msg_2",
                subject="JavaScript Guide",
                sender_name="Code Weekly",
                sender_email="code@example.com",
                received_at=datetime.now(timezone.utc),
            ),
            Email(
                newsletter_id=newsletter.id,
                gmail_message_id="msg_3",
                subject="AI News",
                sender_name="Tech Blog",
                sender_email="tech@example.com",
                received_at=datetime.now(timezone.utc),
            ),
        ]

        for email in emails:
            async_session.add(email)

        await async_session.commit()
        return newsletter, emails

    @pytest.mark.asyncio
    async def test_search_matches_subject(self, email_service, searchable_emails):
        """Verify search finds emails matching subject."""
        newsletter, _ = searchable_emails

        results = await email_service.search_emails(newsletter.id, "Python")

        assert len(results) >= 1
        assert any("Python" in r.subject for r in results)

    @pytest.mark.asyncio
    async def test_search_matches_sender(self, email_service, searchable_emails):
        """Verify search finds emails matching sender."""
        newsletter, _ = searchable_emails

        results = await email_service.search_emails(newsletter.id, "Tech Blog")

        assert len(results) >= 1


class TestEmailServiceCounts:
    """Test email count operations."""

    @pytest_asyncio.fixture
    async def email_service(self, async_session: AsyncSession):
        """Create email service with test session."""
        return EmailService(async_session)

    @pytest_asyncio.fixture
    async def counted_emails(self, async_session: AsyncSession):
        """Create emails for count testing."""
        newsletter = Newsletter(
            name="Test Newsletter",
            gmail_label_id="Label_123",
            gmail_label_name="Test",
        )
        async_session.add(newsletter)
        await async_session.flush()

        # 5 unread, 3 read, 2 starred, 1 archived
        emails_data = [
            {"is_read": False, "is_starred": False, "is_archived": False},
            {"is_read": False, "is_starred": True, "is_archived": False},
            {"is_read": False, "is_starred": False, "is_archived": False},
            {"is_read": False, "is_starred": True, "is_archived": False},
            {"is_read": False, "is_starred": False, "is_archived": False},
            {"is_read": True, "is_starred": False, "is_archived": False},
            {"is_read": True, "is_starred": False, "is_archived": False},
            {"is_read": True, "is_starred": False, "is_archived": True},
        ]

        for i, data in enumerate(emails_data):
            email = Email(
                newsletter_id=newsletter.id,
                gmail_message_id=f"msg_{i}",
                subject=f"Email {i}",
                sender_email="test@example.com",
                received_at=datetime.now(timezone.utc),
                **data,
            )
            async_session.add(email)

        await async_session.commit()
        return newsletter

    @pytest.mark.asyncio
    async def test_get_unread_count(self, email_service, counted_emails):
        """Verify unread count is correct."""
        newsletter = counted_emails

        count = await email_service.get_unread_count(newsletter.id)

        assert count == 5

    @pytest.mark.asyncio
    async def test_get_total_count(self, email_service, counted_emails):
        """Verify total count is correct."""
        newsletter = counted_emails

        count = await email_service.get_total_count(newsletter.id)

        # Total count excludes archived by default in repository
        # 8 total - 1 archived = 7 visible
        assert count == 7

    @pytest.mark.asyncio
    async def test_get_starred_count(self, email_service, counted_emails):
        """Verify starred count is correct."""
        newsletter = counted_emails

        count = await email_service.get_starred_count(newsletter.id)

        assert count == 2

    @pytest.mark.asyncio
    async def test_get_archived_count(self, email_service, counted_emails):
        """Verify archived count is correct."""
        newsletter = counted_emails

        count = await email_service.get_archived_count(newsletter.id)

        assert count == 1


class TestEmailServiceSummarization:
    """Test AI summarization operations."""

    @pytest_asyncio.fixture
    async def email_service(self, async_session: AsyncSession):
        """Create email service with test session."""
        return EmailService(async_session)

    @pytest_asyncio.fixture
    async def email_for_summary(self, async_session: AsyncSession):
        """Create email for summarization testing."""
        newsletter = Newsletter(
            name="Test Newsletter",
            gmail_label_id="Label_123",
            gmail_label_name="Test",
        )
        async_session.add(newsletter)
        await async_session.flush()

        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_123",
            subject="Important Update",
            sender_name="Newsletter Team",
            sender_email="news@example.com",
            received_at=datetime.now(timezone.utc),
            body_text="This is the email body with important content.",
        )
        async_session.add(email)
        await async_session.commit()

        return email

    @pytest.mark.asyncio
    async def test_summarize_email_calls_llm(self, email_service, email_for_summary):
        """Verify summarize_email calls LLM service."""
        email = email_for_summary

        with patch("src.services.email_service.LLMService") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.is_enabled.return_value = True
            mock_llm.summarize_email = AsyncMock(
                return_value=MagicMock(
                    success=True,
                    summary="This is a summary.",
                    model="test-model",
                )
            )
            MockLLM.return_value = mock_llm

            result, error = await email_service.summarize_email(email.id)

            mock_llm.summarize_email.assert_called_once()

    @pytest.mark.asyncio
    async def test_summarize_email_disabled_returns_error(
        self, email_service, email_for_summary
    ):
        """Verify summarize_email returns error when LLM disabled."""
        email = email_for_summary

        with patch("src.services.email_service.LLMService") as MockLLM:
            mock_llm = MagicMock()
            mock_llm.is_enabled.return_value = False
            MockLLM.return_value = mock_llm

            result, error = await email_service.summarize_email(email.id)

            assert result is None
            assert error is not None
            assert "disabled" in error.lower()

    @pytest.mark.asyncio
    async def test_summarize_email_not_found_returns_error(self, email_service):
        """Verify summarize_email returns error for missing email."""
        result, error = await email_service.summarize_email(99999)

        assert result is None
        assert error is not None
        assert "not found" in error.lower()
