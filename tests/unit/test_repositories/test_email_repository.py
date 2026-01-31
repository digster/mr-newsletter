"""Tests for EmailRepository - email data access.

These tests verify the email repository correctly handles
email-specific database operations.
"""

from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.email import Email
from src.models.newsletter import Newsletter
from src.repositories.email_repository import EmailRepository


class TestEmailRepositoryBasic:
    """Test basic email operations."""

    @pytest_asyncio.fixture
    async def newsletter(self, async_session: AsyncSession):
        """Create a sample newsletter."""
        newsletter = Newsletter(
            name="Email Test Newsletter",
            gmail_label_id="Label_email_test",
            gmail_label_name="Email Test",
        )
        async_session.add(newsletter)
        await async_session.flush()
        return newsletter

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create an EmailRepository."""
        return EmailRepository(async_session)

    @pytest.mark.asyncio
    async def test_create_email(self, repo, newsletter, async_session):
        """Verify emails can be created."""
        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_create_1",
            subject="Test Subject",
            sender_email="sender@example.com",
            received_at=datetime.now(timezone.utc),
        )

        created = await repo.create(email)
        await async_session.commit()

        assert created.id is not None
        assert created.subject == "Test Subject"

    @pytest.mark.asyncio
    async def test_get_by_id(self, repo, newsletter, async_session):
        """Verify emails can be fetched by ID."""
        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_get_1",
            subject="Get Test",
            sender_email="sender@example.com",
            received_at=datetime.now(timezone.utc),
        )
        created = await repo.create(email)
        await async_session.commit()

        fetched = await repo.get_by_id(created.id)

        assert fetched is not None
        assert fetched.subject == "Get Test"


class TestEmailRepositoryByGmailId:
    """Test Gmail ID queries."""

    @pytest_asyncio.fixture
    async def newsletter(self, async_session: AsyncSession):
        """Create a sample newsletter."""
        newsletter = Newsletter(
            name="Gmail ID Test",
            gmail_label_id="Label_gmail_id",
            gmail_label_name="Gmail ID Test",
        )
        async_session.add(newsletter)
        await async_session.flush()
        return newsletter

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create an EmailRepository."""
        return EmailRepository(async_session)

    @pytest_asyncio.fixture
    async def sample_email(self, repo, newsletter, async_session):
        """Create a sample email."""
        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_unique_gmail_id",
            subject="Gmail ID Test",
            sender_email="sender@example.com",
            received_at=datetime.now(timezone.utc),
        )
        created = await repo.create(email)
        await async_session.commit()
        return created

    @pytest.mark.asyncio
    async def test_get_by_gmail_id(self, repo, sample_email):
        """Verify emails can be fetched by Gmail message ID."""
        result = await repo.get_by_gmail_id("msg_unique_gmail_id")

        assert result is not None
        assert result.subject == "Gmail ID Test"

    @pytest.mark.asyncio
    async def test_get_by_gmail_id_returns_none_for_missing(self, repo):
        """Verify get_by_gmail_id returns None for nonexistent ID."""
        result = await repo.get_by_gmail_id("nonexistent_gmail_id")

        assert result is None

    @pytest.mark.asyncio
    async def test_exists_by_gmail_id(self, repo, sample_email):
        """Verify exists_by_gmail_id returns True for existing email."""
        result = await repo.exists_by_gmail_id("msg_unique_gmail_id")

        assert result is True

    @pytest.mark.asyncio
    async def test_exists_by_gmail_id_returns_false_for_missing(self, repo):
        """Verify exists_by_gmail_id returns False for nonexistent ID."""
        result = await repo.exists_by_gmail_id("nonexistent_gmail_id")

        assert result is False


class TestEmailRepositoryByNewsletter:
    """Test newsletter-based email queries."""

    @pytest_asyncio.fixture
    async def newsletter(self, async_session: AsyncSession):
        """Create a sample newsletter."""
        newsletter = Newsletter(
            name="Newsletter Query Test",
            gmail_label_id="Label_nl_query",
            gmail_label_name="Newsletter Query",
        )
        async_session.add(newsletter)
        await async_session.flush()
        return newsletter

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create an EmailRepository."""
        return EmailRepository(async_session)

    @pytest_asyncio.fixture
    async def sample_emails(self, repo, newsletter, async_session):
        """Create sample emails with various states."""
        now = datetime.now(timezone.utc)
        emails = [
            Email(
                newsletter_id=newsletter.id,
                gmail_message_id="msg_nl_1",
                subject="Unread Email",
                sender_email="a@example.com",
                received_at=now - timedelta(hours=1),
                is_read=False,
                is_starred=False,
                is_archived=False,
            ),
            Email(
                newsletter_id=newsletter.id,
                gmail_message_id="msg_nl_2",
                subject="Read Email",
                sender_email="b@example.com",
                received_at=now - timedelta(hours=2),
                is_read=True,
                is_starred=False,
                is_archived=False,
            ),
            Email(
                newsletter_id=newsletter.id,
                gmail_message_id="msg_nl_3",
                subject="Starred Email",
                sender_email="c@example.com",
                received_at=now - timedelta(hours=3),
                is_read=False,
                is_starred=True,
                is_archived=False,
            ),
            Email(
                newsletter_id=newsletter.id,
                gmail_message_id="msg_nl_4",
                subject="Archived Email",
                sender_email="d@example.com",
                received_at=now - timedelta(hours=4),
                is_read=True,
                is_starred=False,
                is_archived=True,
            ),
        ]

        for email in emails:
            await repo.create(email)

        await async_session.commit()
        return emails

    @pytest.mark.asyncio
    async def test_get_by_newsletter_pagination(self, repo, newsletter, sample_emails):
        """Verify pagination works correctly."""
        # Get first 2
        page1 = await repo.get_by_newsletter(newsletter.id, limit=2, offset=0)

        # Non-archived emails = 3, so page1 should have 2
        assert len(page1) == 2

    @pytest.mark.asyncio
    async def test_get_by_newsletter_excludes_archived(self, repo, newsletter, sample_emails):
        """Verify archived emails are excluded by default."""
        result = await repo.get_by_newsletter(newsletter.id)

        subjects = [e.subject for e in result]
        assert "Archived Email" not in subjects

    @pytest.mark.asyncio
    async def test_get_by_newsletter_unread_filter(self, repo, newsletter, sample_emails):
        """Verify unread_only filter works."""
        result = await repo.get_by_newsletter(newsletter.id, unread_only=True)

        for email in result:
            assert email.is_read is False

    @pytest.mark.asyncio
    async def test_get_by_newsletter_starred_filter(self, repo, newsletter, sample_emails):
        """Verify starred_only filter works."""
        result = await repo.get_by_newsletter(newsletter.id, starred_only=True)

        for email in result:
            assert email.is_starred is True

    @pytest.mark.asyncio
    async def test_get_by_newsletter_archived_filter(self, repo, newsletter, sample_emails):
        """Verify archived_only filter works."""
        result = await repo.get_by_newsletter(newsletter.id, archived_only=True)

        for email in result:
            assert email.is_archived is True


class TestEmailRepositoryCounts:
    """Test email count operations."""

    @pytest_asyncio.fixture
    async def newsletter(self, async_session: AsyncSession):
        """Create a sample newsletter."""
        newsletter = Newsletter(
            name="Count Test Newsletter",
            gmail_label_id="Label_count_test",
            gmail_label_name="Count Test",
        )
        async_session.add(newsletter)
        await async_session.flush()
        return newsletter

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create an EmailRepository."""
        return EmailRepository(async_session)

    @pytest_asyncio.fixture
    async def counted_emails(self, repo, newsletter, async_session):
        """Create emails for count testing."""
        now = datetime.now(timezone.utc)
        # 3 unread (not archived), 2 read (not archived), 1 starred, 1 archived
        emails = [
            Email(newsletter_id=newsletter.id, gmail_message_id="c1", subject="U1",
                  sender_email="a@x.com", received_at=now, is_read=False, is_archived=False),
            Email(newsletter_id=newsletter.id, gmail_message_id="c2", subject="U2",
                  sender_email="a@x.com", received_at=now, is_read=False, is_archived=False),
            Email(newsletter_id=newsletter.id, gmail_message_id="c3", subject="U3",
                  sender_email="a@x.com", received_at=now, is_read=False, is_starred=True, is_archived=False),
            Email(newsletter_id=newsletter.id, gmail_message_id="c4", subject="R1",
                  sender_email="a@x.com", received_at=now, is_read=True, is_archived=False),
            Email(newsletter_id=newsletter.id, gmail_message_id="c5", subject="R2",
                  sender_email="a@x.com", received_at=now, is_read=True, is_archived=False),
            Email(newsletter_id=newsletter.id, gmail_message_id="c6", subject="A1",
                  sender_email="a@x.com", received_at=now, is_read=True, is_archived=True),
        ]

        for email in emails:
            await repo.create(email)

        await async_session.commit()
        return emails

    @pytest.mark.asyncio
    async def test_get_unread_count(self, repo, newsletter, counted_emails):
        """Verify unread count is correct."""
        count = await repo.get_unread_count(newsletter.id)

        assert count == 3  # 3 unread, non-archived

    @pytest.mark.asyncio
    async def test_get_count(self, repo, newsletter, counted_emails):
        """Verify total count excludes archived."""
        count = await repo.get_count(newsletter.id)

        assert count == 5  # 6 total - 1 archived = 5

    @pytest.mark.asyncio
    async def test_get_starred_count(self, repo, newsletter, counted_emails):
        """Verify starred count is correct."""
        count = await repo.get_starred_count(newsletter.id)

        assert count == 1

    @pytest.mark.asyncio
    async def test_get_archived_count(self, repo, newsletter, counted_emails):
        """Verify archived count is correct."""
        count = await repo.get_archived_count(newsletter.id)

        assert count == 1


class TestEmailRepositoryReadStatus:
    """Test read/unread status operations."""

    @pytest_asyncio.fixture
    async def newsletter(self, async_session: AsyncSession):
        """Create a sample newsletter."""
        newsletter = Newsletter(
            name="Read Status Test",
            gmail_label_id="Label_read_status",
            gmail_label_name="Read Status",
        )
        async_session.add(newsletter)
        await async_session.flush()
        return newsletter

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create an EmailRepository."""
        return EmailRepository(async_session)

    @pytest_asyncio.fixture
    async def sample_email(self, repo, newsletter, async_session):
        """Create a sample unread email."""
        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_read_test",
            subject="Read Status Test",
            sender_email="test@example.com",
            received_at=datetime.now(timezone.utc),
            is_read=False,
        )
        created = await repo.create(email)
        await async_session.commit()
        return created

    @pytest.mark.asyncio
    async def test_mark_as_read(self, repo, sample_email, async_session):
        """Verify mark_as_read sets is_read to True."""
        result = await repo.mark_as_read(sample_email.id)
        await async_session.commit()

        assert result is not None
        assert result.is_read is True
        assert result.read_at is not None

    @pytest.mark.asyncio
    async def test_mark_as_unread(self, repo, sample_email, async_session):
        """Verify mark_as_unread sets is_read to False."""
        # First mark as read
        await repo.mark_as_read(sample_email.id)
        await async_session.commit()

        # Then mark as unread
        result = await repo.mark_as_unread(sample_email.id)
        await async_session.commit()

        assert result is not None
        assert result.is_read is False
        assert result.read_at is None


class TestEmailRepositoryStarred:
    """Test starred toggle operation."""

    @pytest_asyncio.fixture
    async def newsletter(self, async_session: AsyncSession):
        """Create a sample newsletter."""
        newsletter = Newsletter(
            name="Star Test",
            gmail_label_id="Label_star",
            gmail_label_name="Star",
        )
        async_session.add(newsletter)
        await async_session.flush()
        return newsletter

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create an EmailRepository."""
        return EmailRepository(async_session)

    @pytest_asyncio.fixture
    async def sample_email(self, repo, newsletter, async_session):
        """Create a sample email."""
        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_star_test",
            subject="Star Test",
            sender_email="test@example.com",
            received_at=datetime.now(timezone.utc),
            is_starred=False,
        )
        created = await repo.create(email)
        await async_session.commit()
        return created

    @pytest.mark.asyncio
    async def test_toggle_starred_sets_true(self, repo, sample_email, async_session):
        """Verify toggle_starred sets is_starred to True."""
        result = await repo.toggle_starred(sample_email.id)
        await async_session.commit()

        assert result is not None
        assert result.is_starred is True

    @pytest.mark.asyncio
    async def test_toggle_starred_sets_false(self, repo, sample_email, async_session):
        """Verify toggle_starred sets is_starred to False."""
        # Toggle to True
        await repo.toggle_starred(sample_email.id)
        await async_session.commit()

        # Toggle back to False
        result = await repo.toggle_starred(sample_email.id)
        await async_session.commit()

        assert result is not None
        assert result.is_starred is False


class TestEmailRepositoryArchive:
    """Test archive operations."""

    @pytest_asyncio.fixture
    async def newsletter(self, async_session: AsyncSession):
        """Create a sample newsletter."""
        newsletter = Newsletter(
            name="Archive Test",
            gmail_label_id="Label_archive",
            gmail_label_name="Archive",
        )
        async_session.add(newsletter)
        await async_session.flush()
        return newsletter

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create an EmailRepository."""
        return EmailRepository(async_session)

    @pytest_asyncio.fixture
    async def sample_email(self, repo, newsletter, async_session):
        """Create a sample email."""
        email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="msg_archive_test",
            subject="Archive Test",
            sender_email="test@example.com",
            received_at=datetime.now(timezone.utc),
            is_archived=False,
        )
        created = await repo.create(email)
        await async_session.commit()
        return created

    @pytest.mark.asyncio
    async def test_archive(self, repo, sample_email, async_session):
        """Verify archive sets is_archived to True."""
        result = await repo.archive(sample_email.id)
        await async_session.commit()

        assert result is not None
        assert result.is_archived is True

    @pytest.mark.asyncio
    async def test_unarchive(self, repo, sample_email, async_session):
        """Verify unarchive sets is_archived to False."""
        # Archive first
        await repo.archive(sample_email.id)
        await async_session.commit()

        # Unarchive
        result = await repo.unarchive(sample_email.id)
        await async_session.commit()

        assert result is not None
        assert result.is_archived is False


class TestEmailRepositorySearch:
    """Test email search operations."""

    @pytest_asyncio.fixture
    async def newsletter(self, async_session: AsyncSession):
        """Create a sample newsletter."""
        newsletter = Newsletter(
            name="Search Test",
            gmail_label_id="Label_search",
            gmail_label_name="Search",
        )
        async_session.add(newsletter)
        await async_session.flush()
        return newsletter

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create an EmailRepository."""
        return EmailRepository(async_session)

    @pytest_asyncio.fixture
    async def searchable_emails(self, repo, newsletter, async_session):
        """Create searchable emails."""
        now = datetime.now(timezone.utc)
        emails = [
            Email(
                newsletter_id=newsletter.id,
                gmail_message_id="search_1",
                subject="Python Tutorial for Beginners",
                sender_name="Tech Blog",
                sender_email="tech@blog.com",
                received_at=now,
            ),
            Email(
                newsletter_id=newsletter.id,
                gmail_message_id="search_2",
                subject="JavaScript Weekly",
                sender_name="JS News",
                sender_email="js@news.com",
                received_at=now,
            ),
            Email(
                newsletter_id=newsletter.id,
                gmail_message_id="search_3",
                subject="AI and Machine Learning",
                sender_name="Tech Blog",
                sender_email="tech@blog.com",
                received_at=now,
            ),
        ]

        for email in emails:
            await repo.create(email)

        await async_session.commit()
        return emails

    @pytest.mark.asyncio
    async def test_search_matches_subject(self, repo, newsletter, searchable_emails):
        """Verify search matches subject."""
        results = await repo.search(newsletter.id, "Python")

        assert len(results) >= 1
        assert any("Python" in e.subject for e in results)

    @pytest.mark.asyncio
    async def test_search_matches_sender_email(self, repo, newsletter, searchable_emails):
        """Verify search matches sender email."""
        results = await repo.search(newsletter.id, "tech@blog.com")

        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_search_matches_sender_name(self, repo, newsletter, searchable_emails):
        """Verify search matches sender name."""
        results = await repo.search(newsletter.id, "Tech Blog")

        assert len(results) >= 1


class TestEmailRepositoryLatestReceived:
    """Test latest received timestamp query."""

    @pytest_asyncio.fixture
    async def newsletter(self, async_session: AsyncSession):
        """Create a sample newsletter."""
        newsletter = Newsletter(
            name="Latest Test",
            gmail_label_id="Label_latest",
            gmail_label_name="Latest",
        )
        async_session.add(newsletter)
        await async_session.flush()
        return newsletter

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create an EmailRepository."""
        return EmailRepository(async_session)

    @pytest.mark.asyncio
    async def test_get_latest_received_at(self, repo, newsletter, async_session):
        """Verify get_latest_received_at returns most recent timestamp."""
        now = datetime.now(timezone.utc)
        old_time = now - timedelta(days=7)
        new_time = now - timedelta(hours=1)

        # Create old email
        old_email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="old_msg",
            subject="Old",
            sender_email="old@x.com",
            received_at=old_time,
        )
        await repo.create(old_email)

        # Create newer email
        new_email = Email(
            newsletter_id=newsletter.id,
            gmail_message_id="new_msg",
            subject="New",
            sender_email="new@x.com",
            received_at=new_time,
        )
        await repo.create(new_email)
        await async_session.commit()

        result = await repo.get_latest_received_at(newsletter.id)

        assert result is not None
        # Should be closer to new_time than old_time
        assert abs((result.replace(tzinfo=None) - new_time.replace(tzinfo=None)).total_seconds()) < 2

    @pytest.mark.asyncio
    async def test_get_latest_received_at_returns_none_for_empty(self, repo, newsletter):
        """Verify get_latest_received_at returns None for newsletter with no emails."""
        result = await repo.get_latest_received_at(newsletter.id)

        assert result is None
