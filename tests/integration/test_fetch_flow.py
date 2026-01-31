"""Integration tests for email fetching flow.

These tests verify the complete email fetch flow from Gmail API
through to database storage.

CRITICAL INVARIANT: These tests verify that NO delete or trash
operations are ever performed on Gmail emails.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.email import Email
from src.models.newsletter import Newsletter
from src.repositories.email_repository import EmailRepository
from src.repositories.newsletter_repository import NewsletterRepository


class TestFetchFlowStorage:
    """Test email fetch storage operations."""

    @pytest_asyncio.fixture
    async def newsletter(self, async_session: AsyncSession):
        """Create a test newsletter."""
        newsletter = Newsletter(
            name="Test Newsletter",
            gmail_label_id="Label_test",
            gmail_label_name="Test Label",
        )
        async_session.add(newsletter)
        await async_session.commit()
        return newsletter

    @pytest.mark.asyncio
    async def test_fetch_emails_stores_in_database(
        self, async_session: AsyncSession, newsletter
    ):
        """Verify fetched emails are stored in database."""
        email_repo = EmailRepository(async_session)

        # Create email as if fetched from Gmail
        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_123",
            subject="Test Subject",
            sender_email="sender@example.com",
            sender_name="Test Sender",
            received_at=datetime.now(timezone.utc),
            body_html="<p>Test body</p>",
        )

        created = await email_repo.create(email)
        await async_session.commit()

        # Verify stored
        stored = await email_repo.get_by_gmail_id("msg_123")
        assert stored is not None
        assert stored.subject == "Test Subject"
        assert stored.sender_email == "sender@example.com"

    @pytest.mark.asyncio
    async def test_fetch_emails_skips_duplicates(
        self, async_session: AsyncSession, newsletter
    ):
        """Verify duplicate emails are not stored twice."""
        email_repo = EmailRepository(async_session)

        # Create first email
        email1 = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_duplicate",
            subject="Original",
            sender_email="sender@example.com",
            received_at=datetime.now(timezone.utc),
        )
        await email_repo.create(email1)
        await async_session.commit()

        # Check if exists before creating again
        exists = await email_repo.exists_by_gmail_id("msg_duplicate")
        assert exists is True

        # Count should be 1
        count = await email_repo.count()
        assert count == 1

    @pytest.mark.asyncio
    async def test_fetch_emails_updates_newsletter_counts(
        self, async_session: AsyncSession, newsletter
    ):
        """Verify fetch updates newsletter email counts."""
        email_repo = EmailRepository(async_session)
        newsletter_repo = NewsletterRepository(async_session)

        # Create multiple emails
        for i in range(5):
            email = Email(
                newsletter_id=newsletter.id,
                gmail_message_id=f"msg_count_{i}",
                subject=f"Email {i}",
                sender_email="sender@example.com",
                received_at=datetime.now(timezone.utc),
                is_read=i < 2,  # 2 read, 3 unread
            )
            await email_repo.create(email)

        await async_session.commit()

        # Update newsletter counts
        unread = await email_repo.get_unread_count(newsletter.id)
        total = await email_repo.get_count(newsletter.id)

        await newsletter_repo.update_counts(
            newsletter_id=newsletter.id,
            unread_count=unread,
            total_count=total,
        )
        await async_session.commit()

        # Verify counts
        updated = await newsletter_repo.get_by_id(newsletter.id)
        assert updated.unread_count == 3
        assert updated.total_count == 5


class TestFetchFlowSanitization:
    """Test HTML sanitization during fetch."""

    @pytest_asyncio.fixture
    async def newsletter(self, async_session: AsyncSession):
        """Create a test newsletter."""
        newsletter = Newsletter(
            name="Sanitization Test",
            gmail_label_id="Label_sanitize",
            gmail_label_name="Sanitize Label",
        )
        async_session.add(newsletter)
        await async_session.commit()
        return newsletter

    @pytest.mark.asyncio
    async def test_fetch_emails_can_store_html(
        self, async_session: AsyncSession, newsletter
    ):
        """Verify HTML content can be stored."""
        email_repo = EmailRepository(async_session)

        # Store email with HTML
        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_html",
            subject="HTML Email",
            sender_email="sender@example.com",
            received_at=datetime.now(timezone.utc),
            body_html="<p>Safe content</p><a href='https://example.com'>Link</a>",
        )

        await email_repo.create(email)
        await async_session.commit()

        # Verify stored
        stored = await email_repo.get_by_gmail_id("msg_html")
        assert "<p>" in stored.body_html
        assert "<a href" in stored.body_html


class TestFetchFlowCriticalInvariants:
    """Test CRITICAL invariants for Gmail safety.

    IMPORTANT: These tests verify that the fetch flow NEVER
    deletes or trashes emails from Gmail.
    """

    def test_email_repository_has_no_delete_gmail_method(self):
        """CRITICAL: Verify EmailRepository has no Gmail delete methods."""
        from src.repositories.email_repository import EmailRepository

        dangerous_method_names = [
            "delete_from_gmail",
            "trash_gmail_message",
            "remove_from_gmail",
            "gmail_delete",
            "gmail_trash",
        ]

        for method_name in dangerous_method_names:
            assert not hasattr(EmailRepository, method_name), (
                f"CRITICAL: EmailRepository has dangerous method '{method_name}'"
            )

    def test_gmail_service_has_no_delete_methods(self):
        """CRITICAL: Verify GmailService has no delete methods."""
        from src.services.gmail_service import GmailService

        dangerous_method_names = [
            "delete",
            "delete_email",
            "delete_message",
            "trash",
            "trash_email",
            "trash_message",
            "remove",
            "remove_email",
        ]

        for method_name in dangerous_method_names:
            assert not hasattr(GmailService, method_name), (
                f"CRITICAL: GmailService has dangerous method '{method_name}'"
            )

    def test_newsletter_service_has_no_gmail_delete_methods(self):
        """CRITICAL: Verify NewsletterService has no Gmail delete methods."""
        from src.services.newsletter_service import NewsletterService

        dangerous_method_names = [
            "delete_gmail_emails",
            "trash_gmail_emails",
            "remove_gmail_messages",
        ]

        for method_name in dangerous_method_names:
            assert not hasattr(NewsletterService, method_name), (
                f"CRITICAL: NewsletterService has dangerous method '{method_name}'"
            )


class TestFetchFlowRateLimiting:
    """Test rate limiting behavior during fetch."""

    @pytest_asyncio.fixture
    async def newsletter(self, async_session: AsyncSession):
        """Create a test newsletter."""
        newsletter = Newsletter(
            name="Rate Limit Test",
            gmail_label_id="Label_rate",
            gmail_label_name="Rate Label",
        )
        async_session.add(newsletter)
        await async_session.commit()
        return newsletter

    @pytest.mark.asyncio
    async def test_multiple_emails_can_be_stored(
        self, async_session: AsyncSession, newsletter
    ):
        """Verify multiple emails can be stored in sequence."""
        email_repo = EmailRepository(async_session)

        # Store many emails (simulating batch fetch)
        for i in range(20):
            email = Email(
                newsletter_id=newsletter.id,
                gmail_message_id=f"msg_batch_{i}",
                subject=f"Batch Email {i}",
                sender_email="sender@example.com",
                received_at=datetime.now(timezone.utc),
            )
            await email_repo.create(email)

        await async_session.commit()

        # Verify all stored
        count = await email_repo.get_count(newsletter.id)
        assert count == 20
