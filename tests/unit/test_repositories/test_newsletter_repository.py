"""Tests for NewsletterRepository - newsletter data access.

These tests verify the newsletter repository correctly handles
newsletter-specific database operations.
"""

from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.email import Email
from src.models.newsletter import Newsletter
from src.repositories.newsletter_repository import NewsletterRepository


class TestNewsletterRepositoryBasic:
    """Test basic newsletter operations."""

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create a NewsletterRepository."""
        return NewsletterRepository(async_session)

    @pytest.mark.asyncio
    async def test_create_newsletter(self, repo, async_session):
        """Verify newsletters can be created."""
        newsletter = Newsletter(
            name="Tech Weekly",
            gmail_label_id="Label_tech",
            gmail_label_name="Newsletters/Tech",
            description="Weekly tech digest",
        )

        created = await repo.create(newsletter)
        await async_session.commit()

        assert created.id is not None
        assert created.name == "Tech Weekly"

    @pytest.mark.asyncio
    async def test_get_by_id(self, repo, async_session):
        """Verify newsletters can be fetched by ID."""
        newsletter = Newsletter(
            name="News Daily",
            gmail_label_id="Label_news",
            gmail_label_name="News",
        )
        created = await repo.create(newsletter)
        await async_session.commit()

        fetched = await repo.get_by_id(created.id)

        assert fetched is not None
        assert fetched.name == "News Daily"


class TestNewsletterRepositoryByLabelId:
    """Test Gmail label ID queries."""

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create a NewsletterRepository."""
        return NewsletterRepository(async_session)

    @pytest_asyncio.fixture
    async def sample_newsletter(self, repo, async_session):
        """Create a sample newsletter."""
        newsletter = Newsletter(
            name="Label Test",
            gmail_label_id="Label_unique_123",
            gmail_label_name="Test Label",
        )
        created = await repo.create(newsletter)
        await async_session.commit()
        return created

    @pytest.mark.asyncio
    async def test_get_by_gmail_label_id(self, repo, sample_newsletter):
        """Verify newsletters can be fetched by Gmail label ID."""
        result = await repo.get_by_gmail_label_id("Label_unique_123")

        assert result is not None
        assert result.name == "Label Test"

    @pytest.mark.asyncio
    async def test_get_by_gmail_label_id_returns_none_for_missing(self, repo):
        """Verify get_by_gmail_label_id returns None for nonexistent label."""
        result = await repo.get_by_gmail_label_id("nonexistent_label")

        assert result is None

    @pytest.mark.asyncio
    async def test_exists_by_label_id(self, repo, sample_newsletter):
        """Verify exists_by_label_id returns True for existing label."""
        result = await repo.exists_by_label_id("Label_unique_123")

        assert result is True

    @pytest.mark.asyncio
    async def test_exists_by_label_id_returns_false_for_missing(self, repo):
        """Verify exists_by_label_id returns False for nonexistent label."""
        result = await repo.exists_by_label_id("nonexistent_label")

        assert result is False


class TestNewsletterRepositoryActiveStatus:
    """Test active/inactive newsletter filtering."""

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create a NewsletterRepository."""
        return NewsletterRepository(async_session)

    @pytest_asyncio.fixture
    async def sample_newsletters(self, repo, async_session):
        """Create mix of active and inactive newsletters."""
        active1 = Newsletter(
            name="Active 1",
            gmail_label_id="Label_active_1",
            gmail_label_name="Active 1",
            is_active=True,
        )
        active2 = Newsletter(
            name="Active 2",
            gmail_label_id="Label_active_2",
            gmail_label_name="Active 2",
            is_active=True,
        )
        inactive = Newsletter(
            name="Inactive",
            gmail_label_id="Label_inactive",
            gmail_label_name="Inactive",
            is_active=False,
        )

        await repo.create(active1)
        await repo.create(active2)
        await repo.create(inactive)
        await async_session.commit()

        return [active1, active2, inactive]

    @pytest.mark.asyncio
    async def test_get_all_active_excludes_inactive(self, repo, sample_newsletters):
        """Verify get_all_active only returns active newsletters."""
        result = await repo.get_all_active()

        names = [n.name for n in result]
        assert "Active 1" in names
        assert "Active 2" in names
        assert "Inactive" not in names


class TestNewsletterRepositoryAutoFetch:
    """Test auto-fetch enabled queries."""

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create a NewsletterRepository."""
        return NewsletterRepository(async_session)

    @pytest_asyncio.fixture
    async def sample_newsletters(self, repo, async_session):
        """Create newsletters with different auto-fetch settings."""
        auto_enabled = Newsletter(
            name="Auto Fetch Enabled",
            gmail_label_id="Label_auto_1",
            gmail_label_name="Auto 1",
            auto_fetch_enabled=True,
            is_active=True,
        )
        auto_disabled = Newsletter(
            name="Auto Fetch Disabled",
            gmail_label_id="Label_auto_2",
            gmail_label_name="Auto 2",
            auto_fetch_enabled=False,
            is_active=True,
        )
        inactive_auto = Newsletter(
            name="Inactive with Auto",
            gmail_label_id="Label_auto_3",
            gmail_label_name="Auto 3",
            auto_fetch_enabled=True,
            is_active=False,
        )

        await repo.create(auto_enabled)
        await repo.create(auto_disabled)
        await repo.create(inactive_auto)
        await async_session.commit()

        return [auto_enabled, auto_disabled, inactive_auto]

    @pytest.mark.asyncio
    async def test_get_auto_fetch_enabled(self, repo, sample_newsletters):
        """Verify get_auto_fetch_enabled returns correct newsletters."""
        result = await repo.get_auto_fetch_enabled()

        names = [n.name for n in result]
        assert "Auto Fetch Enabled" in names
        assert "Auto Fetch Disabled" not in names
        # Inactive newsletters should be excluded even if auto_fetch is enabled
        assert "Inactive with Auto" not in names


class TestNewsletterRepositoryWithEmails:
    """Test newsletter with emails relationship loading."""

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create a NewsletterRepository."""
        return NewsletterRepository(async_session)

    @pytest_asyncio.fixture
    async def newsletter_with_emails(self, repo, async_session):
        """Create a newsletter with emails."""
        newsletter = Newsletter(
            name="With Emails",
            gmail_label_id="Label_with_emails",
            gmail_label_name="With Emails",
        )
        created = await repo.create(newsletter)
        await async_session.flush()

        # Add emails
        for i in range(3):
            email = Email(
                newsletter_id=created.id,
                gmail_message_id=f"msg_rel_{i}",
                subject=f"Email {i}",
                sender_email="test@example.com",
                received_at=datetime.now(timezone.utc),
            )
            async_session.add(email)

        await async_session.commit()
        return created

    @pytest.mark.asyncio
    async def test_get_with_emails_loads_relationship(
        self, repo, newsletter_with_emails
    ):
        """Verify get_with_emails eagerly loads emails."""
        result = await repo.get_with_emails(newsletter_with_emails.id)

        assert result is not None
        assert hasattr(result, "emails")
        # Emails should be loaded (not lazy)
        assert len(result.emails) == 3


class TestNewsletterRepositoryUpdateCounts:
    """Test email count updates."""

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create a NewsletterRepository."""
        return NewsletterRepository(async_session)

    @pytest_asyncio.fixture
    async def sample_newsletter(self, repo, async_session):
        """Create a sample newsletter."""
        newsletter = Newsletter(
            name="Count Update Test",
            gmail_label_id="Label_count",
            gmail_label_name="Count Label",
            unread_count=0,
            total_count=0,
        )
        created = await repo.create(newsletter)
        await async_session.commit()
        return created

    @pytest.mark.asyncio
    async def test_update_counts(self, repo, sample_newsletter, async_session):
        """Verify update_counts updates both counts."""
        await repo.update_counts(
            newsletter_id=sample_newsletter.id,
            unread_count=5,
            total_count=10,
        )
        await async_session.commit()

        # Fetch fresh to verify
        fresh = await repo.get_by_id(sample_newsletter.id)

        assert fresh.unread_count == 5
        assert fresh.total_count == 10

    @pytest.mark.asyncio
    async def test_update_counts_nonexistent_newsletter(self, repo, async_session):
        """Verify update_counts handles nonexistent newsletter gracefully."""
        # Should not raise
        await repo.update_counts(
            newsletter_id=99999,
            unread_count=5,
            total_count=10,
        )
