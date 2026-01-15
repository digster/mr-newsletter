"""Email entity model."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .newsletter import Newsletter


class Email(Base, TimestampMixin):
    """Email entity representing a newsletter email.

    Stores email metadata and content fetched from Gmail.
    """

    __tablename__ = "emails"

    # Create indexes for common queries
    __table_args__ = (
        Index("idx_email_newsletter_date", "newsletter_id", "received_at"),
        Index("idx_email_gmail_id", "gmail_message_id"),
        Index("idx_email_is_read", "is_read"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Gmail identifiers
    gmail_message_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    # Email metadata
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    sender_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sender_email: Mapped[str] = mapped_column(String(255), nullable=False)
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Content
    snippet: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    body_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Reading status
    is_read: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("0"), nullable=False
    )
    is_starred: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("0"), nullable=False
    )
    is_archived: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("0"), nullable=False
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Size tracking
    size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Newsletter relationship
    newsletter_id: Mapped[int] = mapped_column(
        ForeignKey("newsletters.id"),
        nullable=False,
    )
    newsletter: Mapped["Newsletter"] = relationship(
        "Newsletter",
        back_populates="emails",
    )

    def __repr__(self) -> str:
        subject_preview = (
            self.subject[:30] + "..." if len(self.subject) > 30 else self.subject
        )
        return f"<Email(id={self.id}, subject='{subject_preview}', from='{self.sender_email}')>"
