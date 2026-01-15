"""Newsletter entity model."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from .email import Email


class Newsletter(Base, TimestampMixin):
    """Newsletter subscription entity.

    Represents a newsletter the user wants to track.
    Linked to Gmail via label_id for filtering.
    """

    __tablename__ = "newsletters"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Gmail integration
    gmail_label_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    gmail_label_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Auto-fetch settings
    auto_fetch_enabled: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=text("1"), nullable=False
    )
    fetch_interval_minutes: Mapped[int] = mapped_column(
        Integer,
        default=1440,  # 24 hours
    )

    # Tracking
    last_fetched_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    last_email_received_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    unread_count: Mapped[int] = mapped_column(Integer, default=0)
    total_count: Mapped[int] = mapped_column(Integer, default=0)

    # UI customization
    color: Mapped[Optional[str]] = mapped_column(
        String(7),
        nullable=True,
    )  # Hex color like #FF5733
    icon: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )  # Icon name

    # Status
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=text("1"), nullable=False
    )

    # Relationships
    emails: Mapped[list["Email"]] = relationship(
        "Email",
        back_populates="newsletter",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Newsletter(id={self.id}, name='{self.name}', label='{self.gmail_label_name}')>"
