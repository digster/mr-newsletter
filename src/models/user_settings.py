"""User settings entity model."""

from typing import Optional

from sqlalchemy import Boolean, Float, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class UserSettings(Base, TimestampMixin):
    """User application settings.

    Singleton pattern - only one row should exist.
    """

    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(primary_key=True, default=1)

    # Appearance
    theme_mode: Mapped[str] = mapped_column(
        String(10),
        default="system",
    )  # light, dark, system

    accent_color: Mapped[str] = mapped_column(
        String(7),
        default="#6750A4",
    )  # Material 3 purple

    active_theme: Mapped[Optional[str]] = mapped_column(
        String(255),
        default="default.json",
        nullable=True,
    )  # Active theme filename

    # Fetching
    global_auto_fetch: Mapped[bool] = mapped_column(Boolean, default=True)
    default_fetch_interval: Mapped[int] = mapped_column(
        Integer,
        default=1440,  # 24 hours in minutes
    )
    fetch_queue_delay_seconds: Mapped[int] = mapped_column(
        Integer,
        default=5,
    )

    # Notifications
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # Reading
    mark_read_on_open: Mapped[bool] = mapped_column(Boolean, default=True)

    # User info (cached from Google)
    user_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # LLM Configuration (for AI Summarization)
    llm_enabled: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=text("0"), nullable=False
    )
    llm_api_base_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    llm_api_key_encrypted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    llm_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    llm_max_tokens: Mapped[int] = mapped_column(
        Integer, default=500, server_default=text("500"), nullable=False
    )
    llm_temperature: Mapped[float] = mapped_column(
        Float, default=0.3, server_default=text("0.3"), nullable=False
    )

    def __repr__(self) -> str:
        return f"<UserSettings(theme={self.theme_mode}, active_theme={self.active_theme}, user={self.user_email})>"
