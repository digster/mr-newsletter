"""Email repository for data access."""

from datetime import datetime
from typing import Optional, Sequence

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.email import Email

from .base_repository import BaseRepository


class EmailRepository(BaseRepository[Email]):
    """Repository for Email entity operations."""

    def __init__(self, session: AsyncSession):
        """Initialize email repository.

        Args:
            session: Async database session.
        """
        super().__init__(session, Email)

    async def get_by_gmail_id(self, gmail_message_id: str) -> Optional[Email]:
        """Get email by Gmail message ID.

        Args:
            gmail_message_id: Gmail message ID.

        Returns:
            Email if found, None otherwise.
        """
        result = await self.session.execute(
            select(Email).where(Email.gmail_message_id == gmail_message_id)
        )
        return result.scalar_one_or_none()

    async def exists_by_gmail_id(self, gmail_message_id: str) -> bool:
        """Check if email with Gmail ID exists.

        Args:
            gmail_message_id: Gmail message ID.

        Returns:
            True if exists, False otherwise.
        """
        email = await self.get_by_gmail_id(gmail_message_id)
        return email is not None

    async def get_by_newsletter(
        self,
        newsletter_id: int,
        limit: int = 50,
        offset: int = 0,
        unread_only: bool = False,
        starred_only: bool = False,
    ) -> Sequence[Email]:
        """Get emails for a newsletter.

        Args:
            newsletter_id: Newsletter ID.
            limit: Maximum number of emails to return.
            offset: Number of emails to skip.
            unread_only: If True, only return unread emails.
            starred_only: If True, only return starred emails.

        Returns:
            List of emails.
        """
        query = (
            select(Email)
            .where(Email.newsletter_id == newsletter_id)
            .where(Email.is_archived== False)  # noqa: E712 Non-archived emails
            .order_by(desc(Email.received_at))
            .limit(limit)
            .offset(offset)
        )

        if unread_only:
            query = query.where(Email.is_read== False)  # noqa: E712 Unread emails

        if starred_only:
            query = query.where(Email.is_starred.is_(True))

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_unread_count(self, newsletter_id: int) -> int:
        """Get count of unread emails for a newsletter.

        Args:
            newsletter_id: Newsletter ID.

        Returns:
            Count of unread emails.
        """
        result = await self.session.execute(
            select(func.count())
            .select_from(Email)
            .where(Email.newsletter_id == newsletter_id)
            .where(Email.is_read== False)  # noqa: E712 Unread emails
            .where(Email.is_archived== False)  # noqa: E712 Non-archived emails
        )
        return result.scalar() or 0

    async def get_count(self, newsletter_id: int) -> int:
        """Get total count of emails for a newsletter.

        Args:
            newsletter_id: Newsletter ID.

        Returns:
            Total count of emails.
        """
        result = await self.session.execute(
            select(func.count())
            .select_from(Email)
            .where(Email.newsletter_id == newsletter_id)
            .where(Email.is_archived== False)  # noqa: E712 Non-archived emails
        )
        return result.scalar() or 0

    async def get_starred_count(self, newsletter_id: int) -> int:
        """Get count of starred emails for a newsletter.

        Args:
            newsletter_id: Newsletter ID.

        Returns:
            Count of starred emails.
        """
        result = await self.session.execute(
            select(func.count())
            .select_from(Email)
            .where(Email.newsletter_id == newsletter_id)
            .where(Email.is_starred.is_(True))
            .where(Email.is_archived== False)  # noqa: E712 Non-archived emails
        )
        return result.scalar() or 0

    async def mark_as_read(self, email_id: int) -> Optional[Email]:
        """Mark email as read.

        Args:
            email_id: Email ID.

        Returns:
            Updated email if found, None otherwise.
        """
        email = await self.get_by_id(email_id)
        if email and not email.is_read:
            email.is_read = True
            email.read_at = datetime.utcnow()
            await self.session.flush()
        return email

    async def mark_as_unread(self, email_id: int) -> Optional[Email]:
        """Mark email as unread.

        Args:
            email_id: Email ID.

        Returns:
            Updated email if found, None otherwise.
        """
        email = await self.get_by_id(email_id)
        if email and email.is_read:
            email.is_read = False
            email.read_at = None
            await self.session.flush()
        return email

    async def toggle_starred(self, email_id: int) -> Optional[Email]:
        """Toggle email starred status.

        Args:
            email_id: Email ID.

        Returns:
            Updated email if found, None otherwise.
        """
        email = await self.get_by_id(email_id)
        if email:
            email.is_starred = not email.is_starred
            await self.session.flush()
        return email

    async def archive(self, email_id: int) -> Optional[Email]:
        """Archive an email.

        Args:
            email_id: Email ID.

        Returns:
            Updated email if found, None otherwise.
        """
        email = await self.get_by_id(email_id)
        if email:
            email.is_archived = True
            await self.session.flush()
        return email

    async def get_latest_received_at(
        self,
        newsletter_id: int,
    ) -> Optional[datetime]:
        """Get the most recent received_at timestamp for a newsletter.

        Args:
            newsletter_id: Newsletter ID.

        Returns:
            Most recent timestamp or None if no emails.
        """
        result = await self.session.execute(
            select(func.max(Email.received_at)).where(
                Email.newsletter_id == newsletter_id
            )
        )
        return result.scalar()

    async def search(
        self,
        newsletter_id: int,
        query: str,
        limit: int = 50,
    ) -> Sequence[Email]:
        """Search emails by subject or sender.

        Args:
            newsletter_id: Newsletter ID.
            query: Search query.
            limit: Maximum results.

        Returns:
            Matching emails.
        """
        search_pattern = f"%{query}%"
        result = await self.session.execute(
            select(Email)
            .where(Email.newsletter_id == newsletter_id)
            .where(Email.is_archived== False)  # noqa: E712 Non-archived emails
            .where(
                (Email.subject.ilike(search_pattern))
                | (Email.sender_email.ilike(search_pattern))
                | (Email.sender_name.ilike(search_pattern))
            )
            .order_by(desc(Email.received_at))
            .limit(limit)
        )
        return result.scalars().all()
