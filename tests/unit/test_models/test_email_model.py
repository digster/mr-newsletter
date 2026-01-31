"""Tests for Email model.

These tests verify the Email model's field defaults,
constraints, and relationships.
"""

from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.models.email import Email
from src.models.newsletter import Newsletter


class TestEmailModelCreation:
    """Test Email model creation with defaults."""

    @pytest_asyncio.fixture
    async def newsletter(self, async_session: AsyncSession):
        """Create a parent newsletter."""
        newsletter = Newsletter(
            name="Email Test Newsletter",
            gmail_label_id="Label_email_test",
            gmail_label_name="Email Test Label",
        )
        async_session.add(newsletter)
        await async_session.commit()
        return newsletter

    @pytest.mark.asyncio
    async def test_create_email_with_required_fields(
        self, async_session: AsyncSession, newsletter
    ):
        """Verify email can be created with minimum required fields."""
        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_required",
            subject="Required Fields Email",
            sender_email="sender@example.com",
            received_at=datetime.now(timezone.utc),
        )
        async_session.add(email)
        await async_session.commit()

        assert email.id is not None
        assert email.newsletter_id == newsletter.id
        assert email.subject == "Required Fields Email"

    @pytest.mark.asyncio
    async def test_email_defaults(self, async_session: AsyncSession, newsletter):
        """Verify email has correct default values."""
        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_defaults",
            subject="Default Email",
            sender_email="sender@example.com",
            received_at=datetime.now(timezone.utc),
        )
        async_session.add(email)
        await async_session.commit()

        assert email.is_read is False
        assert email.is_starred is False
        assert email.is_archived is False
        assert email.read_at is None
        assert email.sender_name is None
        assert email.body_html is None
        assert email.body_text is None
        assert email.summary is None

    @pytest.mark.asyncio
    async def test_email_with_all_fields(
        self, async_session: AsyncSession, newsletter
    ):
        """Verify email can be created with all optional fields."""
        received = datetime.now(timezone.utc)
        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_full",
            subject="Full Email",
            sender_email="sender@example.com",
            sender_name="Test Sender",
            received_at=received,
            body_html="<p>HTML body</p>",
            body_text="Plain text body",
            is_read=True,
            is_starred=True,
            is_archived=False,
            summary="This is a summary",
        )
        async_session.add(email)
        await async_session.commit()

        assert email.sender_name == "Test Sender"
        assert email.body_html == "<p>HTML body</p>"
        assert email.body_text == "Plain text body"
        assert email.is_read is True
        assert email.is_starred is True
        assert email.summary == "This is a summary"


class TestEmailModelConstraints:
    """Test Email model constraints."""

    @pytest_asyncio.fixture
    async def newsletter(self, async_session: AsyncSession):
        """Create a parent newsletter."""
        newsletter = Newsletter(
            name="Constraint Test",
            gmail_label_id="Label_constraint",
            gmail_label_name="Constraint Label",
        )
        async_session.add(newsletter)
        await async_session.commit()
        return newsletter

    @pytest.mark.asyncio
    async def test_unique_gmail_message_id_constraint(
        self, async_session: AsyncSession, newsletter
    ):
        """Verify gmail_message_id must be unique."""
        email1 = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_duplicate",
            subject="First",
            sender_email="sender@example.com",
            received_at=datetime.now(timezone.utc),
        )
        async_session.add(email1)
        await async_session.commit()

        email2 = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_duplicate",  # Same message ID
            subject="Second",
            sender_email="sender@example.com",
            received_at=datetime.now(timezone.utc),
        )
        async_session.add(email2)

        with pytest.raises(IntegrityError):
            await async_session.commit()

    @pytest.mark.asyncio
    async def test_newsletter_id_is_required(self, async_session: AsyncSession):
        """Verify newsletter_id field is required for email creation."""
        # This test verifies the field is required, since SQLite FK enforcement
        # is not guaranteed in all test configurations
        email = Email(
            newsletter_id=None,  # type: ignore - testing null constraint
            gmail_message_id="msg_orphan",
            subject="Orphan Email",
            sender_email="sender@example.com",
            received_at=datetime.now(timezone.utc),
        )
        async_session.add(email)

        with pytest.raises(IntegrityError):
            await async_session.commit()


class TestEmailModelRelationships:
    """Test Email model relationships."""

    @pytest_asyncio.fixture
    async def newsletter(self, async_session: AsyncSession):
        """Create a parent newsletter."""
        newsletter = Newsletter(
            name="Relationship Test",
            gmail_label_id="Label_email_rel",
            gmail_label_name="Email Rel Label",
        )
        async_session.add(newsletter)
        await async_session.commit()
        return newsletter

    @pytest.mark.asyncio
    async def test_email_newsletter_relationship(
        self, async_session: AsyncSession, newsletter
    ):
        """Verify email has newsletter relationship."""
        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_rel",
            subject="Relationship Email",
            sender_email="sender@example.com",
            received_at=datetime.now(timezone.utc),
        )
        async_session.add(email)
        await async_session.commit()

        # Refresh to ensure relationship is loaded
        await async_session.refresh(email)

        assert hasattr(email, "newsletter")
        assert email.newsletter.name == "Relationship Test"


class TestEmailModelReadTimestamp:
    """Test read_at timestamp behavior."""

    @pytest_asyncio.fixture
    async def newsletter(self, async_session: AsyncSession):
        """Create a parent newsletter."""
        newsletter = Newsletter(
            name="Read Timestamp Test",
            gmail_label_id="Label_read_ts",
            gmail_label_name="Read TS Label",
        )
        async_session.add(newsletter)
        await async_session.commit()
        return newsletter

    @pytest.mark.asyncio
    async def test_read_at_null_by_default(
        self, async_session: AsyncSession, newsletter
    ):
        """Verify read_at is null for new unread emails."""
        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_unread_ts",
            subject="Unread Email",
            sender_email="sender@example.com",
            received_at=datetime.now(timezone.utc),
        )
        async_session.add(email)
        await async_session.commit()

        assert email.read_at is None
        assert email.is_read is False

    @pytest.mark.asyncio
    async def test_read_at_can_be_set(
        self, async_session: AsyncSession, newsletter
    ):
        """Verify read_at can be set when marking as read."""
        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_read_ts",
            subject="Read Email",
            sender_email="sender@example.com",
            received_at=datetime.now(timezone.utc),
        )
        async_session.add(email)
        await async_session.commit()

        # Mark as read with timestamp
        read_time = datetime.now(timezone.utc)
        email.is_read = True
        email.read_at = read_time
        await async_session.commit()

        assert email.is_read is True
        assert email.read_at is not None


class TestEmailModelRepr:
    """Test Email model string representation."""

    @pytest_asyncio.fixture
    async def newsletter(self, async_session: AsyncSession):
        """Create a parent newsletter."""
        newsletter = Newsletter(
            name="Repr Newsletter",
            gmail_label_id="Label_email_repr",
            gmail_label_name="Email Repr Label",
        )
        async_session.add(newsletter)
        await async_session.commit()
        return newsletter

    @pytest.mark.asyncio
    async def test_email_repr(self, async_session: AsyncSession, newsletter):
        """Verify email __repr__ format."""
        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_repr",
            subject="Repr Test Subject",
            sender_email="sender@example.com",
            received_at=datetime.now(timezone.utc),
        )
        async_session.add(email)
        await async_session.commit()

        repr_str = repr(email)
        assert "Email" in repr_str
        assert "Repr Test Subject" in repr_str
