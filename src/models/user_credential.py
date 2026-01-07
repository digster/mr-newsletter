"""User credential entity model for OAuth tokens."""

from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class UserCredential(Base, TimestampMixin):
    """User OAuth tokens.

    Stores access_token and refresh_token obtained after OAuth flow.
    These are encrypted before storage.
    """

    __tablename__ = "user_credentials"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # User identifier
    user_email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    # OAuth tokens (encrypted)
    access_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token_encrypted: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Token metadata
    token_expiry: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    scopes: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="[]",
    )  # JSON array of scopes

    def __repr__(self) -> str:
        return f"<UserCredential(user_email='{self.user_email}')>"
