"""Data access layer."""

from .base_repository import BaseRepository
from .email_repository import EmailRepository
from .newsletter_repository import NewsletterRepository
from .user_settings_repository import UserSettingsRepository

__all__ = [
    "BaseRepository",
    "EmailRepository",
    "NewsletterRepository",
    "UserSettingsRepository",
]
