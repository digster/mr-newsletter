"""Email service for business logic."""

import logging
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.email import Email
from src.models.user_settings import UserSettings
from src.repositories.email_repository import EmailRepository
from src.repositories.newsletter_repository import NewsletterRepository
from src.services.llm_service import LLMService, get_current_timestamp
from src.utils.html_sanitizer import html_to_plain_text

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
        archived_only: bool = False,
    ) -> Sequence[Email]:
        """Get emails for a newsletter.

        Args:
            newsletter_id: Newsletter ID.
            limit: Maximum emails to return.
            offset: Number of emails to skip.
            unread_only: Only return unread emails.
            starred_only: Only return starred emails.
            archived_only: Only return archived emails.

        Returns:
            List of emails.
        """
        return await self.email_repo.get_by_newsletter(
            newsletter_id=newsletter_id,
            limit=limit,
            offset=offset,
            unread_only=unread_only,
            starred_only=starred_only,
            archived_only=archived_only,
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

    async def unarchive_email(self, email_id: int) -> Optional[Email]:
        """Unarchive an email and update newsletter count.

        Args:
            email_id: Email ID.

        Returns:
            Updated email if found.
        """
        email = await self.email_repo.unarchive(email_id)
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

    async def get_archived_count(self, newsletter_id: int) -> int:
        """Get archived email count for newsletter.

        Args:
            newsletter_id: Newsletter ID.

        Returns:
            Archived count.
        """
        return await self.email_repo.get_archived_count(newsletter_id)

    async def get_filtered_count(
        self,
        newsletter_id: int,
        unread_only: bool = False,
        starred_only: bool = False,
        archived_only: bool = False,
    ) -> int:
        """Get email count with filters applied.

        Args:
            newsletter_id: Newsletter ID.
            unread_only: Only count unread emails.
            starred_only: Only count starred emails.
            archived_only: Only count archived emails.

        Returns:
            Filtered count.
        """
        if archived_only:
            return await self.email_repo.get_archived_count(newsletter_id)
        elif starred_only:
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

    async def summarize_email(
        self,
        email_id: int,
        user_settings: Optional[UserSettings] = None,
    ) -> tuple[Optional[Email], Optional[str]]:
        """Generate AI summary for an email.

        Args:
            email_id: Email ID.
            user_settings: Optional user settings for LLM configuration.

        Returns:
            Tuple of (updated email, error message if any).
        """
        email = await self.email_repo.get_by_id(email_id)
        if not email:
            return None, "Email not found"

        # Initialize LLM service with user settings
        llm_service = LLMService(user_settings=user_settings)

        if not llm_service.is_enabled():
            return None, "AI summarization is disabled. Enable it in Settings."

        # Fallback: convert HTML to text if body_text is empty
        # This handles existing emails synced before the HTML->text extraction fix
        body_text = email.body_text
        if not body_text or not body_text.strip():
            if email.body_html:
                logger.debug(
                    f"Email {email_id} has no body_text, converting HTML to text"
                )
                body_text = html_to_plain_text(email.body_html)
            else:
                body_text = ""

        # Generate summary
        result = await llm_service.summarize_email(
            subject=email.subject,
            body_text=body_text,
            sender_name=email.sender_name,
        )

        if not result.success:
            return None, result.error

        # Save summary to database (keep None if None, don't convert to empty string)
        email = await self.email_repo.update_summary(
            email_id=email_id,
            summary=result.summary,
            model=result.model or "unknown",
            summarized_at=get_current_timestamp(),
        )

        await self.session.commit()

        # Refresh the email object to reload attributes after commit
        # (SQLAlchemy expires objects on commit, causing stale data issues)
        if email:
            await self.session.refresh(email)
            logger.info(
                f"Saved summary: id={email.id}, "
                f"summary_length={len(email.summary) if email.summary else 0}"
            )

        return email, None

    async def clear_email_summary(self, email_id: int) -> Optional[Email]:
        """Clear an email's summary for regeneration.

        Args:
            email_id: Email ID.

        Returns:
            Updated email if found.
        """
        email = await self.email_repo.clear_summary(email_id)
        if email:
            await self.session.commit()
        return email
