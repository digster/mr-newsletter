"""Configuration management using Pydantic Settings."""

import platform
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

    # Database - PostgreSQL (for web mode)
    postgres_database_url: str = Field(
        default="postgresql+asyncpg://newsletter:password@localhost:5432/newsletter",
        description="PostgreSQL connection URL for web mode",
    )

    # Database - SQLite (for desktop mode)
    sqlite_db_name: str = Field(
        default="newsletter.db",
        description="SQLite database filename for desktop mode",
    )

    # Security - Encryption key for credentials in DB
    encryption_key: str = Field(
        default="dev-encryption-key-change-in-production",
        description="32-byte key for encrypting credentials in database",
    )

    # Google OAuth - Optional with empty defaults (app shows config error page if missing)
    google_client_id: str = Field(
        default="",
        description="Google OAuth Client ID from Google Cloud Console",
    )
    google_client_secret: str = Field(
        default="",
        description="Google OAuth Client Secret from Google Cloud Console",
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

    # LLM Configuration (for AI Summarization)
    llm_enabled: bool = Field(
        default=False,
        description="Enable AI-powered email summarization",
    )
    llm_api_base_url: str = Field(
        default="http://localhost:1234/v1",
        description="OpenAI-compatible API base URL (e.g., LM Studio)",
    )
    llm_api_key: str = Field(
        default="",
        description="API key for the LLM service (optional for local LM Studio)",
    )
    llm_model: str = Field(
        default="",
        description="Model name/ID (leave empty for server default)",
    )
    llm_max_tokens: int = Field(
        default=500,
        description="Maximum tokens for summary generation",
    )
    llm_temperature: float = Field(
        default=0.3,
        description="Temperature for LLM responses (lower = more deterministic)",
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
    def is_desktop_mode(self) -> bool:
        """Check if running in desktop mode (uses SQLite)."""
        return not self.flet_web_app

    @property
    def user_data_dir(self) -> Path:
        """Get platform-appropriate user data directory for SQLite database."""
        app_name = "mr-newsletter"
        system = platform.system()

        if system == "Windows":
            base = Path.home() / "AppData" / "Local"
        elif system == "Darwin":  # macOS
            base = Path.home() / "Library" / "Application Support"
        else:  # Linux and others
            base = Path.home() / ".local" / "share"

        data_dir = base / app_name
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir

    @property
    def sqlite_database_path(self) -> Path:
        """Get full path to SQLite database file."""
        return self.user_data_dir / self.sqlite_db_name

    @property
    def database_url(self) -> str:
        """Get appropriate database URL based on mode.

        Desktop mode: SQLite with aiosqlite driver
        Web mode: PostgreSQL with asyncpg driver
        """
        if self.is_desktop_mode:
            return f"sqlite+aiosqlite:///{self.sqlite_database_path}"
        return self.postgres_database_url

    @property
    def sync_database_url(self) -> str:
        """Get synchronous database URL for Alembic migrations."""
        if self.is_desktop_mode:
            return f"sqlite:///{self.sqlite_database_path}"
        return self.postgres_database_url.replace("+asyncpg", "")

    @property
    def is_oauth_configured(self) -> bool:
        """Check if Google OAuth credentials are configured."""
        return bool(self.google_client_id and self.google_client_secret)


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
