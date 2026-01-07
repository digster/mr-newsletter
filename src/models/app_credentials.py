"""App credentials entity model for OAuth client credentials."""

from sqlalchemy import Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class AppCredentials(Base, TimestampMixin):
    """Google OAuth client credentials.

    Stores the client_id and client_secret from Google Cloud Console.
    These are encrypted before storage.
    Singleton pattern - only one row should exist.
    """

    __tablename__ = "app_credentials"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)

    # OAuth client credentials (encrypted)
    client_id_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    client_secret_encrypted: Mapped[str] = mapped_column(Text, nullable=False)

    # Configuration status
    is_configured: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<AppCredentials(configured={self.is_configured})>"
