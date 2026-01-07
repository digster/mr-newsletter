"""Unit tests for NewsletterService."""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.newsletter import Newsletter
from src.services.newsletter_service import NewsletterService


class TestNewsletterService:
    """Tests for NewsletterService."""

    @pytest_asyncio.fixture
    async def service(self, async_session: AsyncSession):
        """Create newsletter service for testing."""
        return NewsletterService(session=async_session)

    @pytest.mark.asyncio
    async def test_create_newsletter(
        self, service: NewsletterService, sample_newsletter_data: dict
    ):
        """Test creating a new newsletter."""
        newsletter = await service.create_newsletter(
            name=sample_newsletter_data["name"],
            gmail_label_id=sample_newsletter_data["gmail_label_id"],
            gmail_label_name=sample_newsletter_data["gmail_label_name"],
            description=sample_newsletter_data["description"],
            auto_fetch=sample_newsletter_data["auto_fetch_enabled"],
            fetch_interval=sample_newsletter_data["fetch_interval_minutes"],
        )

        assert newsletter.id is not None
        assert newsletter.name == sample_newsletter_data["name"]
        assert newsletter.gmail_label_id == sample_newsletter_data["gmail_label_id"]
        assert newsletter.auto_fetch_enabled == sample_newsletter_data["auto_fetch_enabled"]

    @pytest.mark.asyncio
    async def test_get_newsletter(
        self, service: NewsletterService, sample_newsletter_data: dict
    ):
        """Test getting a newsletter by ID."""
        created = await service.create_newsletter(
            name=sample_newsletter_data["name"],
            gmail_label_id=sample_newsletter_data["gmail_label_id"],
            gmail_label_name=sample_newsletter_data["gmail_label_name"],
        )

        retrieved = await service.get_newsletter(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == created.name

    @pytest.mark.asyncio
    async def test_get_all_newsletters(
        self, service: NewsletterService, sample_newsletter_data: dict
    ):
        """Test getting all newsletters."""
        # Create multiple newsletters
        await service.create_newsletter(
            name="Newsletter 1",
            gmail_label_id="label_1",
            gmail_label_name="Label 1",
        )
        await service.create_newsletter(
            name="Newsletter 2",
            gmail_label_id="label_2",
            gmail_label_name="Label 2",
        )

        newsletters = await service.get_all_newsletters()

        assert len(newsletters) == 2

    @pytest.mark.asyncio
    async def test_update_newsletter(
        self, service: NewsletterService, sample_newsletter_data: dict
    ):
        """Test updating a newsletter."""
        created = await service.create_newsletter(
            name=sample_newsletter_data["name"],
            gmail_label_id=sample_newsletter_data["gmail_label_id"],
            gmail_label_name=sample_newsletter_data["gmail_label_name"],
        )

        updated = await service.update_newsletter(
            newsletter_id=created.id,
            name="Updated Name",
            auto_fetch=False,
        )

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.auto_fetch_enabled is False

    @pytest.mark.asyncio
    async def test_delete_newsletter(
        self, service: NewsletterService, sample_newsletter_data: dict
    ):
        """Test deleting a newsletter."""
        created = await service.create_newsletter(
            name=sample_newsletter_data["name"],
            gmail_label_id=sample_newsletter_data["gmail_label_id"],
            gmail_label_name=sample_newsletter_data["gmail_label_name"],
        )

        result = await service.delete_newsletter(created.id)
        assert result is True

        retrieved = await service.get_newsletter(created.id)
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_label_exists(
        self, service: NewsletterService, sample_newsletter_data: dict
    ):
        """Test checking if label exists."""
        await service.create_newsletter(
            name=sample_newsletter_data["name"],
            gmail_label_id=sample_newsletter_data["gmail_label_id"],
            gmail_label_name=sample_newsletter_data["gmail_label_name"],
        )

        exists = await service.label_exists(sample_newsletter_data["gmail_label_id"])
        assert exists is True

        not_exists = await service.label_exists("nonexistent_label")
        assert not_exists is False
