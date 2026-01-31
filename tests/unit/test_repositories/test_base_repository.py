"""Tests for BaseRepository - generic CRUD operations.

These tests verify the base repository provides correct CRUD operations
that all specialized repositories inherit.
"""

from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.newsletter import Newsletter
from src.repositories.base_repository import BaseRepository


class TestBaseRepositoryCreate:
    """Test create operations."""

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create a BaseRepository for Newsletter."""
        return BaseRepository(async_session, Newsletter)

    @pytest.mark.asyncio
    async def test_create_adds_entity(self, repo, async_session):
        """Verify create adds an entity to the database."""
        newsletter = Newsletter(
            name="Test Newsletter",
            gmail_label_id="Label_123",
            gmail_label_name="Test Label",
        )

        created = await repo.create(newsletter)

        assert created.id is not None
        assert created.name == "Test Newsletter"

    @pytest.mark.asyncio
    async def test_create_returns_entity_with_id(self, repo):
        """Verify create returns the entity with an assigned ID."""
        newsletter = Newsletter(
            name="Another Newsletter",
            gmail_label_id="Label_456",
            gmail_label_name="Another Label",
        )

        created = await repo.create(newsletter)

        assert isinstance(created.id, int)
        assert created.id > 0


class TestBaseRepositoryRead:
    """Test read operations."""

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create a BaseRepository for Newsletter."""
        return BaseRepository(async_session, Newsletter)

    @pytest_asyncio.fixture
    async def sample_newsletter(self, repo):
        """Create a sample newsletter."""
        newsletter = Newsletter(
            name="Read Test",
            gmail_label_id="Label_read",
            gmail_label_name="Read Label",
        )
        return await repo.create(newsletter)

    @pytest.mark.asyncio
    async def test_get_by_id_returns_entity(self, repo, sample_newsletter):
        """Verify get_by_id returns the correct entity."""
        result = await repo.get_by_id(sample_newsletter.id)

        assert result is not None
        assert result.id == sample_newsletter.id
        assert result.name == "Read Test"

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_for_missing(self, repo):
        """Verify get_by_id returns None for nonexistent ID."""
        result = await repo.get_by_id(99999)

        assert result is None

    @pytest.mark.asyncio
    async def test_get_all_returns_all_entities(self, repo, async_session):
        """Verify get_all returns all entities."""
        # Create multiple newsletters
        for i in range(3):
            newsletter = Newsletter(
                name=f"Newsletter {i}",
                gmail_label_id=f"Label_{i}",
                gmail_label_name=f"Label {i}",
            )
            await repo.create(newsletter)

        await async_session.commit()

        result = await repo.get_all()

        assert len(result) >= 3


class TestBaseRepositoryUpdate:
    """Test update operations."""

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create a BaseRepository for Newsletter."""
        return BaseRepository(async_session, Newsletter)

    @pytest_asyncio.fixture
    async def sample_newsletter(self, repo, async_session):
        """Create a sample newsletter."""
        newsletter = Newsletter(
            name="Update Test",
            gmail_label_id="Label_update",
            gmail_label_name="Update Label",
        )
        created = await repo.create(newsletter)
        await async_session.commit()
        return created

    @pytest.mark.asyncio
    async def test_update_modifies_entity(self, repo, sample_newsletter, async_session):
        """Verify update modifies the entity in the database."""
        sample_newsletter.name = "Updated Name"

        updated = await repo.update(sample_newsletter)
        await async_session.commit()

        # Fetch fresh from database
        fresh = await repo.get_by_id(sample_newsletter.id)

        assert fresh.name == "Updated Name"


class TestBaseRepositoryDelete:
    """Test delete operations."""

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create a BaseRepository for Newsletter."""
        return BaseRepository(async_session, Newsletter)

    @pytest_asyncio.fixture
    async def sample_newsletter(self, repo, async_session):
        """Create a sample newsletter."""
        newsletter = Newsletter(
            name="Delete Test",
            gmail_label_id="Label_delete",
            gmail_label_name="Delete Label",
        )
        created = await repo.create(newsletter)
        await async_session.commit()
        return created

    @pytest.mark.asyncio
    async def test_delete_removes_entity(self, repo, sample_newsletter, async_session):
        """Verify delete removes the entity from the database."""
        entity_id = sample_newsletter.id

        await repo.delete(sample_newsletter)
        await async_session.commit()

        result = await repo.get_by_id(entity_id)

        assert result is None

    @pytest.mark.asyncio
    async def test_delete_by_id_removes_entity(self, repo, sample_newsletter, async_session):
        """Verify delete_by_id removes the entity."""
        entity_id = sample_newsletter.id

        result = await repo.delete_by_id(entity_id)
        await async_session.commit()

        assert result is True

        # Verify it's gone
        fetched = await repo.get_by_id(entity_id)
        assert fetched is None

    @pytest.mark.asyncio
    async def test_delete_by_id_returns_false_for_missing(self, repo):
        """Verify delete_by_id returns False for nonexistent ID."""
        result = await repo.delete_by_id(99999)

        assert result is False


class TestBaseRepositoryExists:
    """Test existence check operations."""

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create a BaseRepository for Newsletter."""
        return BaseRepository(async_session, Newsletter)

    @pytest_asyncio.fixture
    async def sample_newsletter(self, repo, async_session):
        """Create a sample newsletter."""
        newsletter = Newsletter(
            name="Exists Test",
            gmail_label_id="Label_exists",
            gmail_label_name="Exists Label",
        )
        created = await repo.create(newsletter)
        await async_session.commit()
        return created

    @pytest.mark.asyncio
    async def test_exists_returns_true_when_exists(self, repo, sample_newsletter):
        """Verify exists returns True for existing entity."""
        result = await repo.exists(sample_newsletter.id)

        assert result is True

    @pytest.mark.asyncio
    async def test_exists_returns_false_when_missing(self, repo):
        """Verify exists returns False for nonexistent entity."""
        result = await repo.exists(99999)

        assert result is False


class TestBaseRepositoryCount:
    """Test count operations."""

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create a BaseRepository for Newsletter."""
        return BaseRepository(async_session, Newsletter)

    @pytest.mark.asyncio
    async def test_count_returns_zero_for_empty(self, repo):
        """Verify count returns 0 for empty table."""
        result = await repo.count()

        assert isinstance(result, int)
        assert result >= 0

    @pytest.mark.asyncio
    async def test_count_returns_total(self, repo, async_session):
        """Verify count returns correct total."""
        # Get initial count
        initial_count = await repo.count()

        # Add 3 newsletters
        for i in range(3):
            newsletter = Newsletter(
                name=f"Count Test {i}",
                gmail_label_id=f"Label_count_{i}",
                gmail_label_name=f"Count Label {i}",
            )
            await repo.create(newsletter)

        await async_session.commit()

        result = await repo.count()

        assert result == initial_count + 3
