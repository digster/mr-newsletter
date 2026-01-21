"""Gmail API service for fetching emails and labels."""

import asyncio
import base64
import logging
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Optional

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

logger = logging.getLogger(__name__)


@dataclass
class GmailLabel:
    """Gmail label information."""

    id: str
    name: str
    message_count: int
    label_type: str  # system or user


@dataclass
class GmailMessage:
    """Gmail message details."""

    id: str
    thread_id: str
    subject: str
    sender_name: Optional[str]
    sender_email: str
    received_at: datetime
    snippet: str
    body_text: Optional[str]
    body_html: Optional[str]
    size_bytes: int


class GmailService:
    """Service for interacting with Gmail API."""

    def __init__(self, credentials: Credentials):
        """Initialize Gmail service.

        Args:
            credentials: OAuth credentials for Gmail API.
        """
        self.service = build("gmail", "v1", credentials=credentials)

    def get_user_email(self) -> str:
        """Get the authenticated user's email address.

        Returns:
            User's email address.
        """
        try:
            profile = self.service.users().getProfile(userId="me").execute()
            return profile.get("emailAddress", "")
        except HttpError as e:
            logger.error(f"Failed to get user email: {e}")
            return ""

    def get_labels(self, user_labels_only: bool = True) -> list[GmailLabel]:
        """Fetch all labels from Gmail.

        Args:
            user_labels_only: If True, only return user-created labels.

        Returns:
            List of GmailLabel objects.
        """
        try:
            results = self.service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])

            gmail_labels = []
            for label in labels:
                label_type = label.get("type", "user")

                # Skip system labels if only user labels requested
                if user_labels_only and label_type == "system":
                    continue

                # Get detailed label info including message count
                try:
                    label_detail = (
                        self.service.users()
                        .labels()
                        .get(userId="me", id=label["id"])
                        .execute()
                    )

                    gmail_labels.append(
                        GmailLabel(
                            id=label["id"],
                            name=label["name"],
                            message_count=label_detail.get("messagesTotal", 0),
                            label_type=label_type,
                        )
                    )
                except HttpError:
                    # Skip labels we can't get details for
                    continue

            # Sort by name
            gmail_labels.sort(key=lambda x: x.name)
            return gmail_labels
        except HttpError as e:
            logger.error(f"Failed to fetch labels: {e}")
            return []

    def get_messages_by_label(
        self,
        label_id: str,
        max_results: int = 50,
        page_token: Optional[str] = None,
        after_date: Optional[datetime] = None,
    ) -> tuple[list[str], Optional[str]]:
        """Fetch message IDs for a label.

        Args:
            label_id: Gmail label ID.
            max_results: Maximum messages to fetch.
            page_token: Token for pagination.
            after_date: Only fetch messages after this date.

        Returns:
            Tuple of (message_ids, next_page_token).
        """
        try:
            query_parts = []
            if after_date:
                query_parts.append(f"after:{after_date.strftime('%Y/%m/%d')}")

            query = " ".join(query_parts) if query_parts else None

            kwargs = {
                "userId": "me",
                "labelIds": [label_id],
                "maxResults": max_results,
            }
            if page_token:
                kwargs["pageToken"] = page_token
            if query:
                kwargs["q"] = query

            results = self.service.users().messages().list(**kwargs).execute()

            messages = results.get("messages", [])
            message_ids = [msg["id"] for msg in messages]
            next_page = results.get("nextPageToken")

            return message_ids, next_page
        except HttpError as e:
            logger.error(f"Failed to fetch messages: {e}")
            return [], None

    def get_message_detail(self, message_id: str) -> Optional[GmailMessage]:
        """Fetch full message details.

        Args:
            message_id: Gmail message ID.

        Returns:
            GmailMessage if successful, None otherwise.
        """
        try:
            message = (
                self.service.users()
                .messages()
                .get(userId="me", id=message_id, format="full")
                .execute()
            )

            headers = {
                h["name"].lower(): h["value"]
                for h in message["payload"].get("headers", [])
            }

            # Parse sender
            from_header = headers.get("from", "")
            sender_name, sender_email = self._parse_from_header(from_header)

            # Parse date
            date_str = headers.get("date", "")
            try:
                received_at = parsedate_to_datetime(date_str) if date_str else None
            except Exception:
                received_at = None

            if not received_at:
                # Use internal date as fallback
                internal_date = message.get("internalDate")
                if internal_date:
                    received_at = datetime.fromtimestamp(int(internal_date) / 1000)
                else:
                    received_at = datetime.utcnow()

            # Extract body
            body_text, body_html = self._extract_body(message["payload"])

            return GmailMessage(
                id=message["id"],
                thread_id=message["threadId"],
                subject=headers.get("subject", "(No Subject)"),
                sender_name=sender_name,
                sender_email=sender_email,
                received_at=received_at,
                snippet=message.get("snippet", ""),
                body_text=body_text,
                body_html=body_html,
                size_bytes=message.get("sizeEstimate", 0),
            )
        except HttpError as e:
            logger.error(f"Failed to fetch message {message_id}: {e}")
            return None

    def _parse_from_header(self, from_header: str) -> tuple[Optional[str], str]:
        """Parse 'Name <email>' format.

        Args:
            from_header: From header value.

        Returns:
            Tuple of (name, email).
        """
        import re

        # Try "Name <email@domain.com>" format
        match = re.match(r'"?([^"<]*)"?\s*<([^>]+)>', from_header)
        if match:
            name = match.group(1).strip()
            email = match.group(2).strip()
            return name if name else None, email

        # Just an email address
        email = from_header.strip()
        return None, email

    def _extract_body(
        self,
        payload: dict,
    ) -> tuple[Optional[str], Optional[str]]:
        """Extract text and HTML body from message payload.

        Args:
            payload: Message payload.

        Returns:
            Tuple of (body_text, body_html).
        """
        body_text = None
        body_html = None

        def process_part(part: dict) -> None:
            nonlocal body_text, body_html
            mime_type = part.get("mimeType", "")

            if "body" in part and "data" in part["body"]:
                try:
                    data = base64.urlsafe_b64decode(part["body"]["data"]).decode(
                        "utf-8", errors="ignore"
                    )
                    if mime_type == "text/plain" and not body_text:
                        body_text = data
                    elif mime_type == "text/html" and not body_html:
                        body_html = data
                except Exception as e:
                    logger.warning(f"Failed to decode body part: {e}")

            # Process nested parts
            for sub_part in part.get("parts", []):
                process_part(sub_part)

        process_part(payload)
        return body_text, body_html

    def get_message_count_for_label(self, label_id: str) -> int:
        """Get total message count for a label.

        Args:
            label_id: Gmail label ID.

        Returns:
            Total message count.
        """
        try:
            label = (
                self.service.users().labels().get(userId="me", id=label_id).execute()
            )
            return label.get("messagesTotal", 0)
        except HttpError as e:
            logger.error(f"Failed to get label info: {e}")
            return 0

    # =========================================================================
    # Async wrappers for Gmail API calls
    # These prevent event loop starvation on macOS by running blocking I/O
    # in a thread pool, allowing the main thread to process system events.
    # =========================================================================

    async def get_user_email_async(self) -> str:
        """Async version of get_user_email.

        Returns:
            User's email address.
        """
        return await asyncio.to_thread(self.get_user_email)

    async def get_labels_async(self, user_labels_only: bool = True) -> list[GmailLabel]:
        """Async version of get_labels.

        Args:
            user_labels_only: If True, only return user-created labels.

        Returns:
            List of GmailLabel objects.
        """
        return await asyncio.to_thread(self.get_labels, user_labels_only)

    async def get_messages_by_label_async(
        self,
        label_id: str,
        max_results: int = 50,
        page_token: Optional[str] = None,
        after_date: Optional[datetime] = None,
    ) -> tuple[list[str], Optional[str]]:
        """Async version of get_messages_by_label.

        Args:
            label_id: Gmail label ID.
            max_results: Maximum messages to fetch.
            page_token: Token for pagination.
            after_date: Only fetch messages after this date.

        Returns:
            Tuple of (message_ids, next_page_token).
        """
        return await asyncio.to_thread(
            self.get_messages_by_label, label_id, max_results, page_token, after_date
        )

    async def get_message_detail_async(self, message_id: str) -> Optional[GmailMessage]:
        """Async version of get_message_detail.

        Args:
            message_id: Gmail message ID.

        Returns:
            GmailMessage if successful, None otherwise.
        """
        return await asyncio.to_thread(self.get_message_detail, message_id)

    async def get_message_count_for_label_async(self, label_id: str) -> int:
        """Async version of get_message_count_for_label.

        Args:
            label_id: Gmail label ID.

        Returns:
            Total message count.
        """
        return await asyncio.to_thread(self.get_message_count_for_label, label_id)
