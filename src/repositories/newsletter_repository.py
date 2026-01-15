"""Newsletter repository for data access."""

from typing import Optional, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.newsletter import Newsletter

from .base_repository import BaseRepository


class NewsletterRepository(BaseRepository[Newsletter]):
    """Repository for Newsletter entity operations."""

    def __init__(self, session: AsyncSession):
        """Initialize newsletter repository.

        Args:
            session: Async database session.
        """
        super().__init__(session, Newsletter)

    async def get_by_gmail_label_id(self, label_id: str) -> Optional[Newsletter]:
        """Get newsletter by Gmail label ID.

        Args:
            label_id: Gmail label ID.

        Returns:
            Newsletter if found, None otherwise.
        """
        result = await self.session.execute(
            select(Newsletter).where(Newsletter.gmail_label_id == label_id)
        )
        return result.scalar_one_or_none()

    async def get_all_active(self) -> Sequence[Newsletter]:
        """Get all active newsletters.

        Returns:
            List of active newsletters.
        """
        result = await self.session.execute(
            select(Newsletter)
            .where(Newsletter.is_active.is_(True))
            .order_by(Newsletter.name)
        )
        return result.scalars().all()

    async def get_with_emails(self, newsletter_id: int) -> Optional[Newsletter]:
        """Get newsletter with its emails loaded.

        Args:
            newsletter_id: Newsletter ID.

        Returns:
            Newsletter with emails if found, None otherwise.
        """
        result = await self.session.execute(
            select(Newsletter)
            .options(selectinload(Newsletter.emails))
            .where(Newsletter.id == newsletter_id)
        )
        return result.scalar_one_or_none()

    async def get_auto_fetch_enabled(self) -> Sequence[Newsletter]:
        """Get all newsletters with auto-fetch enabled.

        Returns:
            List of newsletters with auto-fetch enabled.
        """
        result = await self.session.execute(
            select(Newsletter)
            .where(Newsletter.is_active.is_(True))
            .where(Newsletter.auto_fetch_enabled.is_(True))
        )
        return result.scalars().all()

    async def update_counts(
        self,
        newsletter_id: int,
        unread_count: int,
        total_count: int,
    ) -> None:
        """Update newsletter email counts.

        Args:
            newsletter_id: Newsletter ID.
            unread_count: New unread count.
            total_count: New total count.
        """
        newsletter = await self.get_by_id(newsletter_id)
        if newsletter:
            newsletter.unread_count = unread_count
            newsletter.total_count = total_count
            await self.session.flush()

    async def exists_by_label_id(self, label_id: str) -> bool:
        """Check if newsletter with label ID exists.

        Args:
            label_id: Gmail label ID.

        Returns:
            True if exists, False otherwise.
        """
        newsletter = await self.get_by_gmail_label_id(label_id)
        return newsletter is not None
