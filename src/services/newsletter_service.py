"""Newsletter service for business logic."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.email import Email
from src.models.newsletter import Newsletter
from src.repositories.email_repository import EmailRepository
from src.repositories.newsletter_repository import NewsletterRepository

from .gmail_service import GmailMessage, GmailService

logger = logging.getLogger(__name__)


class NewsletterService:
    """Service for newsletter business logic."""

    def __init__(
        self,
        session: AsyncSession,
        gmail_service: Optional[GmailService] = None,
    ):
        """Initialize newsletter service.

        Args:
            session: Async database session.
            gmail_service: Gmail service for API calls.
        """
        self.session = session
        self.newsletter_repo = NewsletterRepository(session)
        self.email_repo = EmailRepository(session)
        self.gmail_service = gmail_service

    async def create_newsletter(
        self,
        name: str,
        gmail_label_id: str,
        gmail_label_name: str,
        description: Optional[str] = None,
        auto_fetch: bool = True,
        fetch_interval: int = 1440,
        color: Optional[str] = None,
    ) -> Newsletter:
        """Create a new newsletter.

        Args:
            name: Newsletter name.
            gmail_label_id: Gmail label ID.
            gmail_label_name: Gmail label name.
            description: Optional description.
            auto_fetch: Enable auto-fetch.
            fetch_interval: Fetch interval in minutes.
            color: Optional hex color.

        Returns:
            Created newsletter.
        """
        newsletter = Newsletter(
            name=name,
            gmail_label_id=gmail_label_id,
            gmail_label_name=gmail_label_name,
            description=description,
            auto_fetch_enabled=auto_fetch,
            fetch_interval_minutes=fetch_interval,
            color=color,
        )
        result = await self.newsletter_repo.create(newsletter)
        await self.session.commit()
        return result

    async def get_newsletter(self, newsletter_id: int) -> Optional[Newsletter]:
        """Get newsletter by ID.

        Args:
            newsletter_id: Newsletter ID.

        Returns:
            Newsletter if found.
        """
        return await self.newsletter_repo.get_by_id(newsletter_id)

    async def get_all_newsletters(self) -> Sequence[Newsletter]:
        """Get all active newsletters with updated counts.

        Returns:
            List of newsletters.
        """
        newsletters = await self.newsletter_repo.get_all_active()

        # Update counts and last email received for each newsletter
        for newsletter in newsletters:
            newsletter.unread_count = await self.email_repo.get_unread_count(
                newsletter.id
            )
            newsletter.total_count = await self.email_repo.get_count(newsletter.id)
            newsletter.last_email_received_at = (
                await self.email_repo.get_latest_received_at(newsletter.id)
            )

        return newsletters

    async def update_newsletter(
        self,
        newsletter_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        auto_fetch: Optional[bool] = None,
        fetch_interval: Optional[int] = None,
        color: Optional[str] = None,
    ) -> Optional[Newsletter]:
        """Update newsletter settings.

        Args:
            newsletter_id: Newsletter ID.
            name: New name.
            description: New description.
            auto_fetch: Enable/disable auto-fetch.
            fetch_interval: New fetch interval.
            color: New color.

        Returns:
            Updated newsletter if found.
        """
        newsletter = await self.newsletter_repo.get_by_id(newsletter_id)
        if not newsletter:
            return None

        if name is not None:
            newsletter.name = name
        if description is not None:
            newsletter.description = description
        if auto_fetch is not None:
            newsletter.auto_fetch_enabled = auto_fetch
        if fetch_interval is not None:
            newsletter.fetch_interval_minutes = fetch_interval
        if color is not None:
            newsletter.color = color

        result = await self.newsletter_repo.update(newsletter)
        await self.session.commit()
        return result

    async def delete_newsletter(self, newsletter_id: int) -> bool:
        """Delete a newsletter and all its emails.

        Args:
            newsletter_id: Newsletter ID.

        Returns:
            True if deleted.
        """
        result = await self.newsletter_repo.delete_by_id(newsletter_id)
        await self.session.commit()
        return result

    async def fetch_newsletter_emails(
        self,
        newsletter_id: int,
        max_results: int = 50,
    ) -> int:
        """Fetch new emails for a newsletter from Gmail.

        Uses async Gmail API wrappers to prevent event loop starvation
        on macOS, which causes "Application Not Responding" dialogs.

        Args:
            newsletter_id: Newsletter ID.
            max_results: Maximum emails to fetch.

        Returns:
            Number of new emails fetched.
        """
        if not self.gmail_service:
            raise ValueError("Gmail service not initialized")

        newsletter = await self.newsletter_repo.get_by_id(newsletter_id)
        if not newsletter:
            raise ValueError(f"Newsletter {newsletter_id} not found")

        # Get message IDs (async to prevent blocking)
        message_ids, _ = await self.gmail_service.get_messages_by_label_async(
            label_id=newsletter.gmail_label_id,
            max_results=max_results,
            after_date=newsletter.last_fetched_at,
        )

        new_count = 0
        skipped_existing = 0
        skipped_fetch_failed = 0

        logger.info(f"Got {len(message_ids)} message IDs from Gmail for {newsletter.name}")

        # Process messages with periodic yielding to keep event loop responsive
        for i, msg_id in enumerate(message_ids):
            # Yield to event loop periodically to prevent macOS ANR
            if i > 0 and i % 5 == 0:
                await asyncio.sleep(0)

            if await self.email_repo.exists_by_gmail_id(msg_id):
                skipped_existing += 1
                continue

            # Fetch message detail (async to prevent blocking)
            gmail_msg = await self.gmail_service.get_message_detail_async(msg_id)
            if not gmail_msg:
                skipped_fetch_failed += 1
                logger.warning(f"Failed to fetch message detail for {msg_id}")
                continue

            # Create and save email
            email = self._gmail_message_to_email(gmail_msg, newsletter_id)
            try:
                await self.email_repo.create(email)
                new_count += 1
            except Exception as e:
                logger.error(f"Failed to save email {msg_id}: {e}")
                skipped_fetch_failed += 1

        logger.info(
            f"Fetch summary for {newsletter.name}: {new_count} new, "
            f"{skipped_existing} already existed, {skipped_fetch_failed} fetch failed"
        )

        # Update newsletter tracking
        newsletter.last_fetched_at = datetime.now(timezone.utc)
        newsletter.total_count = await self.email_repo.get_count(newsletter_id)
        newsletter.unread_count = await self.email_repo.get_unread_count(newsletter_id)
        newsletter.last_email_received_at = await self.email_repo.get_latest_received_at(
            newsletter_id
        )
        await self.newsletter_repo.update(newsletter)

        await self.session.commit()

        logger.info(f"Fetched {new_count} new emails for newsletter {newsletter.name}")
        return new_count

    def _gmail_message_to_email(
        self,
        gmail_msg: GmailMessage,
        newsletter_id: int,
    ) -> Email:
        """Convert Gmail message to Email entity.

        Args:
            gmail_msg: Gmail message data.
            newsletter_id: Newsletter ID.

        Returns:
            Email entity.
        """
        return Email(
            gmail_message_id=gmail_msg.id,
            subject=gmail_msg.subject,
            sender_name=gmail_msg.sender_name,
            sender_email=gmail_msg.sender_email,
            received_at=gmail_msg.received_at,
            snippet=gmail_msg.snippet,
            body_text=gmail_msg.body_text,
            body_html=gmail_msg.body_html,
            size_bytes=gmail_msg.size_bytes,
            newsletter_id=newsletter_id,
        )

    async def label_exists(self, label_id: str) -> bool:
        """Check if a newsletter with this label already exists.

        Args:
            label_id: Gmail label ID.

        Returns:
            True if exists.
        """
        return await self.newsletter_repo.exists_by_label_id(label_id)
