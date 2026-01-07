"""Configuration management using Pydantic Settings."""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Environment
    environment: Literal["development", "production", "test"] = Field(
        default="development",
        description="Runtime environment",
    )
    debug: bool = Field(default=False)

    # Paths
    base_dir: Path = Field(
        default_factory=lambda: Path(__file__).parent.parent.parent,
    )

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://newsletter:password@localhost:5432/newsletter",
        description="PostgreSQL connection URL",
    )

    # Security - Encryption key for credentials in DB
    encryption_key: str = Field(
        default="dev-encryption-key-change-in-production",
        description="32-byte key for encrypting credentials in database",
    )

    # Flet UI
    flet_host: str = Field(default="127.0.0.1")
    flet_port: int = Field(default=8550)
    flet_web_app: bool = Field(
        default=False,
        description="Run as web app instead of desktop",
    )
    flet_hot_reload: bool = Field(default=False)

    # Scheduler
    scheduler_enabled: bool = Field(default=True)
    default_fetch_interval: int = Field(
        default=1440,
        description="Default fetch interval in minutes (1440 = 24 hours)",
    )
    fetch_queue_delay_seconds: int = Field(
        default=5,
        description="Delay between fetching different newsletters",
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
    )
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    @field_validator("encryption_key")
    @classmethod
    def validate_encryption_key(cls, v: str) -> str:
        """Ensure encryption key is provided in production."""
        if len(v) < 16:
            raise ValueError("Encryption key must be at least 16 characters")
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    @property
    def is_test(self) -> bool:
        """Check if running in test environment."""
        return self.environment == "test"

    @property
    def sync_database_url(self) -> str:
        """Get synchronous database URL for Alembic migrations."""
        return self.database_url.replace("+asyncpg", "")


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
