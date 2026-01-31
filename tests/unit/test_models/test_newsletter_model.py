"""Tests for Newsletter model.

These tests verify the Newsletter model's field defaults,
constraints, and relationships.
"""

from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.models.newsletter import Newsletter
from src.models.email import Email


class TestNewsletterModelCreation:
    """Test Newsletter model creation with defaults."""

    @pytest.mark.asyncio
    async def test_create_newsletter_with_required_fields(
        self, async_session: AsyncSession
    ):
        """Verify newsletter can be created with minimum required fields."""
        newsletter = Newsletter(
            name="Test Newsletter",
            gmail_label_id="Label_123",
            gmail_label_name="Test Label",
        )
        async_session.add(newsletter)
        await async_session.commit()

        assert newsletter.id is not None
        assert newsletter.name == "Test Newsletter"
        assert newsletter.gmail_label_id == "Label_123"

    @pytest.mark.asyncio
    async def test_newsletter_defaults(self, async_session: AsyncSession):
        """Verify newsletter has correct default values."""
        newsletter = Newsletter(
            name="Default Test",
            gmail_label_id="Label_defaults",
            gmail_label_name="Default Label",
        )
        async_session.add(newsletter)
        await async_session.commit()

        assert newsletter.is_active is True
        assert newsletter.auto_fetch_enabled is True
        assert newsletter.fetch_interval_minutes == 1440  # 24 hours
        assert newsletter.unread_count == 0
        assert newsletter.total_count == 0
        assert newsletter.description is None
        assert newsletter.color is None
        assert newsletter.icon is None

    @pytest.mark.asyncio
    async def test_newsletter_with_all_fields(self, async_session: AsyncSession):
        """Verify newsletter can be created with all optional fields."""
        newsletter = Newsletter(
            name="Full Newsletter",
            gmail_label_id="Label_full",
            gmail_label_name="Full Label",
            description="A complete newsletter description",
            auto_fetch_enabled=False,
            fetch_interval_minutes=60,
            color="#FF5733",
            color_secondary="#3357FF",
            icon="star",
            is_active=True,
        )
        async_session.add(newsletter)
        await async_session.commit()

        assert newsletter.description == "A complete newsletter description"
        assert newsletter.auto_fetch_enabled is False
        assert newsletter.fetch_interval_minutes == 60
        assert newsletter.color == "#FF5733"
        assert newsletter.color_secondary == "#3357FF"
        assert newsletter.icon == "star"


class TestNewsletterModelConstraints:
    """Test Newsletter model constraints."""

    @pytest.mark.asyncio
    async def test_unique_gmail_label_id_constraint(self, async_session: AsyncSession):
        """Verify gmail_label_id must be unique."""
        newsletter1 = Newsletter(
            name="First",
            gmail_label_id="Label_unique",
            gmail_label_name="Unique Label",
        )
        async_session.add(newsletter1)
        await async_session.commit()

        newsletter2 = Newsletter(
            name="Second",
            gmail_label_id="Label_unique",  # Same label ID
            gmail_label_name="Another Label",
        )
        async_session.add(newsletter2)

        with pytest.raises(IntegrityError):
            await async_session.commit()

    @pytest.mark.asyncio
    async def test_name_is_required(self, async_session: AsyncSession):
        """Verify name field is required."""
        newsletter = Newsletter(
            name=None,  # type: ignore
            gmail_label_id="Label_noname",
            gmail_label_name="No Name Label",
        )
        async_session.add(newsletter)

        with pytest.raises(IntegrityError):
            await async_session.commit()


class TestNewsletterModelRelationships:
    """Test Newsletter model relationships."""

    @pytest_asyncio.fixture
    async def newsletter(self, async_session: AsyncSession):
        """Create a test newsletter."""
        newsletter = Newsletter(
            name="Relationship Test",
            gmail_label_id="Label_rel",
            gmail_label_name="Rel Label",
        )
        async_session.add(newsletter)
        await async_session.commit()
        return newsletter

    @pytest.mark.asyncio
    async def test_newsletter_email_relationship(
        self, async_session: AsyncSession, newsletter
    ):
        """Verify newsletter has emails relationship."""
        # Add emails
        for i in range(3):
            email = Email(
                newsletter_id=newsletter.id,
                gmail_message_id=f"msg_model_{i}",
                subject=f"Model Email {i}",
                sender_email="test@example.com",
                received_at=datetime.now(timezone.utc),
            )
            async_session.add(email)

        await async_session.commit()

        # Refresh to load relationship
        await async_session.refresh(newsletter)

        assert hasattr(newsletter, "emails")
        assert len(newsletter.emails) == 3

    @pytest.mark.asyncio
    async def test_cascade_delete_emails(
        self, async_session: AsyncSession, newsletter
    ):
        """Verify deleting newsletter cascades to emails."""
        # Add an email
        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_cascade",
            subject="Cascade Email",
            sender_email="test@example.com",
            received_at=datetime.now(timezone.utc),
        )
        async_session.add(email)
        await async_session.commit()

        email_id = email.id

        # Delete newsletter
        await async_session.delete(newsletter)
        await async_session.commit()

        # Email should be gone
        from sqlalchemy import select

        result = await async_session.execute(
            select(Email).where(Email.id == email_id)
        )
        assert result.scalar_one_or_none() is None


class TestNewsletterModelRepr:
    """Test Newsletter model string representation."""

    @pytest.mark.asyncio
    async def test_newsletter_repr(self, async_session: AsyncSession):
        """Verify newsletter __repr__ format."""
        newsletter = Newsletter(
            name="Repr Test",
            gmail_label_id="Label_repr",
            gmail_label_name="Repr Label",
        )
        async_session.add(newsletter)
        await async_session.commit()

        repr_str = repr(newsletter)
        assert "Newsletter" in repr_str
        assert "Repr Test" in repr_str
        assert "Repr Label" in repr_str
