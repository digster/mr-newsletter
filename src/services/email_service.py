"""Email service for business logic."""

import logging
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.email import Email
from src.repositories.email_repository import EmailRepository
from src.repositories.newsletter_repository import NewsletterRepository

logger = logging.getLogger(__name__)


class EmailService:
    """Service for email business logic."""

    def __init__(self, session: AsyncSession):
        """Initialize email service.

        Args:
            session: Async database session.
        """
        self.session = session
        self.email_repo = EmailRepository(session)
        self.newsletter_repo = NewsletterRepository(session)

    async def get_email(self, email_id: int) -> Optional[Email]:
        """Get email by ID.

        Args:
            email_id: Email ID.

        Returns:
            Email if found.
        """
        return await self.email_repo.get_by_id(email_id)

    async def get_emails_for_newsletter(
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
            limit: Maximum emails to return.
            offset: Number of emails to skip.
            unread_only: Only return unread emails.
            starred_only: Only return starred emails.

        Returns:
            List of emails.
        """
        return await self.email_repo.get_by_newsletter(
            newsletter_id=newsletter_id,
            limit=limit,
            offset=offset,
            unread_only=unread_only,
            starred_only=starred_only,
        )

    async def mark_as_read(self, email_id: int) -> Optional[Email]:
        """Mark email as read and update newsletter count.

        Args:
            email_id: Email ID.

        Returns:
            Updated email if found.
        """
        email = await self.email_repo.mark_as_read(email_id)
        if email:
            # Update newsletter unread count
            await self._update_newsletter_count(email.newsletter_id)
            await self.session.commit()
        return email

    async def mark_as_unread(self, email_id: int) -> Optional[Email]:
        """Mark email as unread and update newsletter count.

        Args:
            email_id: Email ID.

        Returns:
            Updated email if found.
        """
        email = await self.email_repo.mark_as_unread(email_id)
        if email:
            await self._update_newsletter_count(email.newsletter_id)
            await self.session.commit()
        return email

    async def toggle_starred(self, email_id: int) -> Optional[Email]:
        """Toggle email starred status.

        Args:
            email_id: Email ID.

        Returns:
            Updated email if found.
        """
        email = await self.email_repo.toggle_starred(email_id)
        if email:
            await self.session.commit()
        return email

    async def archive_email(self, email_id: int) -> Optional[Email]:
        """Archive an email and update newsletter count.

        Args:
            email_id: Email ID.

        Returns:
            Updated email if found.
        """
        email = await self.email_repo.archive(email_id)
        if email:
            await self._update_newsletter_count(email.newsletter_id)
            await self.session.commit()
        return email

    async def search_emails(
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
        return await self.email_repo.search(
            newsletter_id=newsletter_id,
            query=query,
            limit=limit,
        )

    async def get_unread_count(self, newsletter_id: int) -> int:
        """Get unread email count for newsletter.

        Args:
            newsletter_id: Newsletter ID.

        Returns:
            Unread count.
        """
        return await self.email_repo.get_unread_count(newsletter_id)

    async def get_total_count(self, newsletter_id: int) -> int:
        """Get total email count for newsletter.

        Args:
            newsletter_id: Newsletter ID.

        Returns:
            Total count.
        """
        return await self.email_repo.get_count(newsletter_id)

    async def get_starred_count(self, newsletter_id: int) -> int:
        """Get starred email count for newsletter.

        Args:
            newsletter_id: Newsletter ID.

        Returns:
            Starred count.
        """
        return await self.email_repo.get_starred_count(newsletter_id)

    async def get_filtered_count(
        self,
        newsletter_id: int,
        unread_only: bool = False,
        starred_only: bool = False,
    ) -> int:
        """Get email count with filters applied.

        Args:
            newsletter_id: Newsletter ID.
            unread_only: Only count unread emails.
            starred_only: Only count starred emails.

        Returns:
            Filtered count.
        """
        if starred_only:
            return await self.email_repo.get_starred_count(newsletter_id)
        elif unread_only:
            return await self.email_repo.get_unread_count(newsletter_id)
        else:
            return await self.email_repo.get_count(newsletter_id)

    async def _update_newsletter_count(self, newsletter_id: int) -> None:
        """Update newsletter unread count.

        Args:
            newsletter_id: Newsletter ID.
        """
        unread_count = await self.email_repo.get_unread_count(newsletter_id)
        total_count = await self.email_repo.get_count(newsletter_id)
        await self.newsletter_repo.update_counts(
            newsletter_id,
            unread_count,
            total_count,
        )

    async def get_next_email(
        self,
        newsletter_id: int,
        current_email_id: int,
    ) -> Optional[Email]:
        """Get the next email in the list.

        Args:
            newsletter_id: Newsletter ID.
            current_email_id: Current email ID.

        Returns:
            Next email if found.
        """
        current_email = await self.email_repo.get_by_id(current_email_id)
        if not current_email:
            return None

        emails = await self.email_repo.get_by_newsletter(
            newsletter_id=newsletter_id,
            limit=2,
            offset=0,
        )

        # Find current email and return next
        for i, email in enumerate(emails):
            if email.id == current_email_id and i + 1 < len(emails):
                return emails[i + 1]

        return None

    async def get_previous_email(
        self,
        newsletter_id: int,
        current_email_id: int,
    ) -> Optional[Email]:
        """Get the previous email in the list.

        Args:
            newsletter_id: Newsletter ID.
            current_email_id: Current email ID.

        Returns:
            Previous email if found.
        """
        current_email = await self.email_repo.get_by_id(current_email_id)
        if not current_email:
            return None

        emails = await self.email_repo.get_by_newsletter(
            newsletter_id=newsletter_id,
            limit=100,  # Get enough to find previous
            offset=0,
        )

        # Find current email and return previous
        for i, email in enumerate(emails):
            if email.id == current_email_id and i > 0:
                return emails[i - 1]

        return None
