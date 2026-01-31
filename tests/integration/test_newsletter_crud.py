"""Integration tests for newsletter CRUD operations.

These tests verify newsletter creation, updates, and deletion
work correctly across the repository and service layers.

CRITICAL INVARIANT: Newsletter deletion NEVER affects Gmail emails.
"""

from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.email import Email
from src.models.newsletter import Newsletter
from src.repositories.email_repository import EmailRepository
from src.repositories.newsletter_repository import NewsletterRepository


class TestNewsletterCreate:
    """Test newsletter creation flow."""

    @pytest.mark.asyncio
    async def test_create_newsletter_with_defaults(self, async_session: AsyncSession):
        """Verify newsletter creation with default values."""
        repo = NewsletterRepository(async_session)

        newsletter = Newsletter(
            name="New Newsletter",
            gmail_label_id="Label_new",
            gmail_label_name="New Label",
        )

        created = await repo.create(newsletter)
        await async_session.commit()

        assert created.id is not None
        assert created.is_active is True
        assert created.auto_fetch_enabled is True  # Model default is True
        assert created.unread_count == 0
        assert created.total_count == 0

    @pytest.mark.asyncio
    async def test_create_newsletter_and_add_emails(self, async_session: AsyncSession):
        """Verify newsletter can have emails added after creation."""
        newsletter_repo = NewsletterRepository(async_session)
        email_repo = EmailRepository(async_session)

        # Create newsletter
        newsletter = Newsletter(
            name="With Emails",
            gmail_label_id="Label_with_emails",
            gmail_label_name="With Emails",
        )
        created_newsletter = await newsletter_repo.create(newsletter)
        await async_session.commit()

        # Add emails
        for i in range(3):
            email = Email(
                newsletter_id=created_newsletter.id,
                gmail_message_id=f"msg_crud_{i}",
                subject=f"CRUD Email {i}",
                sender_email="test@example.com",
                received_at=datetime.now(timezone.utc),
            )
            await email_repo.create(email)

        await async_session.commit()

        # Verify via relationship loading
        with_emails = await newsletter_repo.get_with_emails(created_newsletter.id)
        assert len(with_emails.emails) == 3


class TestNewsletterUpdate:
    """Test newsletter update operations."""

    @pytest_asyncio.fixture
    async def newsletter(self, async_session: AsyncSession):
        """Create a test newsletter."""
        newsletter = Newsletter(
            name="Update Test",
            gmail_label_id="Label_update_test",
            gmail_label_name="Update Label",
        )
        async_session.add(newsletter)
        await async_session.commit()
        return newsletter

    @pytest.mark.asyncio
    async def test_update_newsletter_name(
        self, async_session: AsyncSession, newsletter
    ):
        """Verify newsletter name can be updated."""
        repo = NewsletterRepository(async_session)

        newsletter.name = "Updated Name"
        await repo.update(newsletter)
        await async_session.commit()

        fetched = await repo.get_by_id(newsletter.id)
        assert fetched.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_auto_fetch_settings(
        self, async_session: AsyncSession, newsletter
    ):
        """Verify auto-fetch settings can be updated."""
        repo = NewsletterRepository(async_session)

        newsletter.auto_fetch_enabled = True
        newsletter.auto_fetch_interval_minutes = 30
        await repo.update(newsletter)
        await async_session.commit()

        fetched = await repo.get_by_id(newsletter.id)
        assert fetched.auto_fetch_enabled is True
        assert fetched.auto_fetch_interval_minutes == 30


class TestNewsletterDelete:
    """Test newsletter deletion operations.

    CRITICAL: Deletion must only affect local database, NEVER Gmail.
    """

    @pytest_asyncio.fixture
    async def newsletter_with_emails(self, async_session: AsyncSession):
        """Create a newsletter with emails."""
        newsletter = Newsletter(
            name="Delete Test",
            gmail_label_id="Label_delete_test",
            gmail_label_name="Delete Label",
        )
        async_session.add(newsletter)
        await async_session.flush()

        for i in range(5):
            email = Email(
                newsletter_id=newsletter.id,
                gmail_message_id=f"msg_delete_{i}",
                subject=f"Delete Email {i}",
                sender_email="test@example.com",
                received_at=datetime.now(timezone.utc),
            )
            async_session.add(email)

        await async_session.commit()
        return newsletter

    @pytest.mark.asyncio
    async def test_delete_newsletter_removes_from_database(
        self, async_session: AsyncSession, newsletter_with_emails
    ):
        """Verify newsletter is removed from database."""
        repo = NewsletterRepository(async_session)

        await repo.delete(newsletter_with_emails)
        await async_session.commit()

        fetched = await repo.get_by_id(newsletter_with_emails.id)
        assert fetched is None

    @pytest.mark.asyncio
    async def test_delete_newsletter_cascades_to_local_emails(
        self, async_session: AsyncSession, newsletter_with_emails
    ):
        """Verify local emails are deleted with newsletter."""
        newsletter_repo = NewsletterRepository(async_session)
        email_repo = EmailRepository(async_session)
        newsletter_id = newsletter_with_emails.id

        # Verify emails exist before delete
        count_before = await email_repo.get_count(newsletter_id)
        assert count_before == 5

        # Delete newsletter
        await newsletter_repo.delete(newsletter_with_emails)
        await async_session.commit()

        # Emails should be gone (cascade delete)
        # Note: We can't query by newsletter_id anymore since FK is gone
        # Instead verify by gmail_id
        for i in range(5):
            email = await email_repo.get_by_gmail_id(f"msg_delete_{i}")
            assert email is None


class TestNewsletterCriticalInvariants:
    """Test CRITICAL invariants for newsletter operations.

    IMPORTANT: Newsletter operations must NEVER delete Gmail emails.
    """

    def test_newsletter_repository_has_no_gmail_delete_method(self):
        """CRITICAL: Verify NewsletterRepository has no Gmail delete methods."""
        dangerous_method_names = [
            "delete_gmail_emails",
            "remove_gmail_messages",
            "trash_gmail_emails",
            "delete_from_gmail",
        ]

        for method_name in dangerous_method_names:
            assert not hasattr(NewsletterRepository, method_name), (
                f"CRITICAL: NewsletterRepository has dangerous method '{method_name}'"
            )

    def test_email_repository_delete_is_local_only(self):
        """CRITICAL: Verify EmailRepository delete only affects local DB."""
        # The delete method from BaseRepository only affects local DB
        from src.repositories.base_repository import BaseRepository

        # Verify it uses SQLAlchemy session.delete, not Gmail API
        import inspect

        source = inspect.getsource(BaseRepository.delete)
        assert "session.delete" in source
        assert "gmail" not in source.lower()


class TestNewsletterDeactivation:
    """Test newsletter deactivation as alternative to deletion."""

    @pytest_asyncio.fixture
    async def active_newsletter(self, async_session: AsyncSession):
        """Create an active newsletter."""
        newsletter = Newsletter(
            name="Deactivate Test",
            gmail_label_id="Label_deactivate",
            gmail_label_name="Deactivate Label",
            is_active=True,
        )
        async_session.add(newsletter)
        await async_session.commit()
        return newsletter

    @pytest.mark.asyncio
    async def test_deactivate_newsletter_preserves_emails(
        self, async_session: AsyncSession, active_newsletter
    ):
        """Verify deactivation preserves emails while hiding newsletter."""
        repo = NewsletterRepository(async_session)
        email_repo = EmailRepository(async_session)

        # Add an email
        email = Email(
            newsletter_id=active_newsletter.id,
            gmail_message_id="msg_deactivate",
            subject="Preserved Email",
            sender_email="test@example.com",
            received_at=datetime.now(timezone.utc),
        )
        await email_repo.create(email)
        await async_session.commit()

        # Deactivate instead of delete
        active_newsletter.is_active = False
        await repo.update(active_newsletter)
        await async_session.commit()

        # Newsletter should not appear in active list
        active_list = await repo.get_all_active()
        active_ids = [n.id for n in active_list]
        assert active_newsletter.id not in active_ids

        # But email should still exist
        preserved = await email_repo.get_by_gmail_id("msg_deactivate")
        assert preserved is not None
        assert preserved.subject == "Preserved Email"
