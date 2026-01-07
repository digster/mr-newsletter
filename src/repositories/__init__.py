"""Data access layer."""

from .base_repository import BaseRepository
from .newsletter_repository import NewsletterRepository
from .email_repository import EmailRepository

__all__ = [
    "BaseRepository",
    "NewsletterRepository",
    "EmailRepository",
]
