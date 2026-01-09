"""Test data factories for creating sample test objects."""

from datetime import datetime, timezone
from typing import Optional


def create_newsletter(
    id: int = 1,
    name: str = "Test Newsletter",
    gmail_label_id: str = "Label_1",
    gmail_label_name: str = "Newsletters/Test",
    description: Optional[str] = "Test newsletter description",
    unread_count: int = 5,
    total_count: int = 25,
    color: Optional[str] = "#6750A4",
    auto_fetch_enabled: bool = True,
    fetch_interval_minutes: int = 1440,
    is_active: bool = True,
    last_fetched_at: Optional[datetime] = None,
):
    """Factory for creating test Newsletter objects.

    Args:
        id: Newsletter ID.
        name: Newsletter name.
        gmail_label_id: Gmail label ID.
        gmail_label_name: Gmail label name.
        description: Newsletter description.
        unread_count: Number of unread emails.
        total_count: Total number of emails.
        color: Hex color for UI.
        auto_fetch_enabled: Whether auto-fetch is enabled.
        fetch_interval_minutes: Fetch interval in minutes.
        is_active: Whether newsletter is active.
        last_fetched_at: Last fetch timestamp.

    Returns:
        Newsletter model instance.
    """
    from src.models.newsletter import Newsletter

    newsletter = Newsletter(
        id=id,
        name=name,
        gmail_label_id=gmail_label_id,
        gmail_label_name=gmail_label_name,
        description=description,
        unread_count=unread_count,
        total_count=total_count,
        color=color,
        auto_fetch_enabled=auto_fetch_enabled,
        fetch_interval_minutes=fetch_interval_minutes,
        is_active=is_active,
        last_fetched_at=last_fetched_at,
    )
    return newsletter


def create_email(
    id: int = 1,
    newsletter_id: int = 1,
    gmail_message_id: Optional[str] = None,
    subject: str = "Test Email Subject",
    sender_name: str = "Test Sender",
    sender_email: str = "sender@test.com",
    snippet: str = "This is a test email snippet...",
    body_text: str = "Full email body text content.",
    body_html: str = "<p>Full email body HTML content.</p>",
    is_read: bool = False,
    is_starred: bool = False,
    is_archived: bool = False,
    received_at: Optional[datetime] = None,
    size_bytes: int = 1024,
):
    """Factory for creating test Email objects.

    Args:
        id: Email ID.
        newsletter_id: Associated newsletter ID.
        gmail_message_id: Gmail message ID.
        subject: Email subject.
        sender_name: Sender display name.
        sender_email: Sender email address.
        snippet: Email snippet/preview.
        body_text: Plain text body.
        body_html: HTML body.
        is_read: Read status.
        is_starred: Starred status.
        is_archived: Archived status.
        received_at: Received timestamp.
        size_bytes: Email size in bytes.

    Returns:
        Email model instance.
    """
    from src.models.email import Email

    email = Email(
        id=id,
        newsletter_id=newsletter_id,
        gmail_message_id=gmail_message_id or f"msg_{id}",
        subject=subject,
        sender_name=sender_name,
        sender_email=sender_email,
        snippet=snippet,
        body_text=body_text,
        body_html=body_html,
        is_read=is_read,
        is_starred=is_starred,
        is_archived=is_archived,
        received_at=received_at or datetime.now(timezone.utc),
        size_bytes=size_bytes,
    )
    return email


def create_gmail_label(
    id: str = "Label_1",
    name: str = "Test Label",
    message_count: int = 10,
    label_type: str = "user",
):
    """Factory for creating test GmailLabel objects.

    Args:
        id: Label ID.
        name: Label name.
        message_count: Number of messages with this label.
        label_type: Label type (user or system).

    Returns:
        GmailLabel dataclass instance.
    """
    from src.services.gmail_service import GmailLabel

    return GmailLabel(
        id=id,
        name=name,
        message_count=message_count,
        label_type=label_type,
    )


def create_gmail_message(
    id: str = "msg_1",
    thread_id: str = "thread_1",
    subject: str = "Test Gmail Message",
    sender_name: Optional[str] = "Test Sender",
    sender_email: str = "sender@test.com",
    received_at: Optional[datetime] = None,
    snippet: str = "Test snippet...",
    body_text: Optional[str] = "Test body text",
    body_html: Optional[str] = "<p>Test body HTML</p>",
    size_bytes: int = 1024,
):
    """Factory for creating test GmailMessage objects.

    Args:
        id: Message ID.
        thread_id: Thread ID.
        subject: Message subject.
        sender_name: Sender display name.
        sender_email: Sender email.
        received_at: Received timestamp.
        snippet: Message snippet.
        body_text: Plain text body.
        body_html: HTML body.
        size_bytes: Message size.

    Returns:
        GmailMessage dataclass instance.
    """
    from src.services.gmail_service import GmailMessage

    return GmailMessage(
        id=id,
        thread_id=thread_id,
        subject=subject,
        sender_name=sender_name,
        sender_email=sender_email,
        received_at=received_at or datetime.now(timezone.utc),
        snippet=snippet,
        body_text=body_text,
        body_html=body_html,
        size_bytes=size_bytes,
    )


def create_sample_newsletters(count: int = 3) -> list:
    """Create a list of sample newsletters.

    Args:
        count: Number of newsletters to create.

    Returns:
        List of Newsletter instances.
    """
    colors = ["#6750A4", "#E91E63", "#4CAF50", "#FF9800", "#2196F3"]
    newsletters = []

    for i in range(1, count + 1):
        newsletters.append(
            create_newsletter(
                id=i,
                name=f"Newsletter {i}",
                gmail_label_id=f"Label_{i}",
                gmail_label_name=f"Newsletters/Newsletter{i}",
                unread_count=i * 2,
                total_count=i * 10,
                color=colors[(i - 1) % len(colors)],
            )
        )

    return newsletters


def create_sample_emails(newsletter_id: int = 1, count: int = 5) -> list:
    """Create a list of sample emails for a newsletter.

    Args:
        newsletter_id: Newsletter ID to associate emails with.
        count: Number of emails to create.

    Returns:
        List of Email instances.
    """
    emails = []
    now = datetime.now(timezone.utc)

    for i in range(1, count + 1):
        emails.append(
            create_email(
                id=i,
                newsletter_id=newsletter_id,
                subject=f"Test Email #{i}",
                sender_name=f"Sender {i}",
                sender_email=f"sender{i}@test.com",
                snippet=f"This is the snippet for email #{i}...",
                is_read=i % 2 == 0,  # Alternate read/unread
                is_starred=i % 3 == 0,  # Every third is starred
                received_at=now,
            )
        )

    return emails


def create_sample_gmail_labels(count: int = 5) -> list:
    """Create a list of sample Gmail labels.

    Args:
        count: Number of labels to create.

    Returns:
        List of GmailLabel instances.
    """
    labels = []
    label_names = [
        "Newsletters/Tech",
        "Newsletters/Finance",
        "Newsletters/News",
        "Newsletters/Sports",
        "Newsletters/Entertainment",
    ]

    for i in range(min(count, len(label_names))):
        labels.append(
            create_gmail_label(
                id=f"Label_{i + 1}",
                name=label_names[i],
                message_count=(i + 1) * 10,
            )
        )

    return labels
