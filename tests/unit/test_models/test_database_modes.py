"""Tests for dual database mode support (SQLite for desktop, PostgreSQL for web)."""

from datetime import UTC
from pathlib import Path
from unittest.mock import patch

import pytest


class TestDatabaseModeSettings:
    """Test database mode detection and URL generation in settings."""

    def test_desktop_mode_when_flet_web_app_false(self, monkeypatch):
        """Desktop mode should be active when FLET_WEB_APP is false."""
        monkeypatch.setenv("FLET_WEB_APP", "false")
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-id")
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")

        # Clear cached settings
        from src.config.settings import get_settings

        get_settings.cache_clear()

        settings = get_settings()
        assert settings.is_desktop_mode is True
        assert settings.flet_web_app is False

    def test_web_mode_when_flet_web_app_true(self, monkeypatch):
        """Web mode should be active when FLET_WEB_APP is true."""
        monkeypatch.setenv("FLET_WEB_APP", "true")
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-id")
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")

        from src.config.settings import get_settings

        get_settings.cache_clear()

        settings = get_settings()
        assert settings.is_desktop_mode is False
        assert settings.flet_web_app is True

    def test_desktop_mode_uses_sqlite_url(self, monkeypatch):
        """Desktop mode should use SQLite database URL."""
        monkeypatch.setenv("FLET_WEB_APP", "false")
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-id")
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")

        from src.config.settings import get_settings

        get_settings.cache_clear()

        settings = get_settings()
        assert "sqlite" in settings.database_url
        assert "aiosqlite" in settings.database_url
        assert "newsletter.db" in settings.database_url

    def test_web_mode_uses_postgresql_url(self, monkeypatch):
        """Web mode should use PostgreSQL database URL."""
        monkeypatch.setenv("FLET_WEB_APP", "true")
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-id")
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")

        from src.config.settings import get_settings

        get_settings.cache_clear()

        settings = get_settings()
        assert "postgresql" in settings.database_url
        assert "asyncpg" in settings.database_url

    def test_sqlite_sync_url_for_desktop_mode(self, monkeypatch):
        """Desktop mode sync URL should use plain SQLite driver."""
        monkeypatch.setenv("FLET_WEB_APP", "false")
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-id")
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")

        from src.config.settings import get_settings

        get_settings.cache_clear()

        settings = get_settings()
        sync_url = settings.sync_database_url

        assert sync_url.startswith("sqlite:///")
        assert "aiosqlite" not in sync_url

    def test_postgresql_sync_url_for_web_mode(self, monkeypatch):
        """Web mode sync URL should use plain PostgreSQL driver."""
        monkeypatch.setenv("FLET_WEB_APP", "true")
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-id")
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")

        from src.config.settings import get_settings

        get_settings.cache_clear()

        settings = get_settings()
        sync_url = settings.sync_database_url

        assert "postgresql://" in sync_url
        assert "asyncpg" not in sync_url

    def test_sqlite_database_path_in_user_data_dir(self, monkeypatch):
        """SQLite database path should be in the user data directory."""
        monkeypatch.setenv("FLET_WEB_APP", "false")
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-id")
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")

        from src.config.settings import get_settings

        get_settings.cache_clear()

        settings = get_settings()
        db_path = settings.sqlite_database_path

        assert db_path.parent == settings.user_data_dir
        assert db_path.name == "newsletter.db"

    def test_custom_sqlite_db_name(self, monkeypatch):
        """Custom SQLite database name should be respected."""
        monkeypatch.setenv("FLET_WEB_APP", "false")
        monkeypatch.setenv("SQLITE_DB_NAME", "custom.db")
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-id")
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")

        from src.config.settings import get_settings

        get_settings.cache_clear()

        settings = get_settings()
        assert settings.sqlite_database_path.name == "custom.db"
        assert "custom.db" in settings.database_url

    def test_user_data_dir_macos(self, monkeypatch):
        """User data directory should use macOS path on Darwin."""
        monkeypatch.setenv("FLET_WEB_APP", "false")
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-id")
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")

        from src.config.settings import get_settings

        get_settings.cache_clear()

        with patch("platform.system", return_value="Darwin"):
            # Need to reimport to use patched platform
            from src.config import settings as settings_module

            settings_module.get_settings.cache_clear()
            settings = settings_module.get_settings()

            # On macOS, should use Library/Application Support
            expected_base = Path.home() / "Library" / "Application Support" / "mr-newsletter"
            assert settings.user_data_dir == expected_base

    def test_user_data_dir_linux(self, monkeypatch):
        """User data directory should use XDG path on Linux."""
        monkeypatch.setenv("FLET_WEB_APP", "false")
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-id")
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")

        from src.config.settings import get_settings

        get_settings.cache_clear()

        with patch("platform.system", return_value="Linux"):
            from src.config import settings as settings_module

            settings_module.get_settings.cache_clear()
            settings = settings_module.get_settings()

            expected_base = Path.home() / ".local" / "share" / "mr-newsletter"
            assert settings.user_data_dir == expected_base

    def test_user_data_dir_windows(self, monkeypatch):
        """User data directory should use AppData on Windows."""
        monkeypatch.setenv("FLET_WEB_APP", "false")
        monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-id")
        monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "test-secret")

        from src.config.settings import get_settings

        get_settings.cache_clear()

        with patch("platform.system", return_value="Windows"):
            from src.config import settings as settings_module

            settings_module.get_settings.cache_clear()
            settings = settings_module.get_settings()

            expected_base = Path.home() / "AppData" / "Local" / "mr-newsletter"
            assert settings.user_data_dir == expected_base


class TestTimestampMixin:
    """Test that TimestampMixin works with SQLite."""

    @pytest.mark.asyncio
    async def test_created_at_default(self, async_session):
        """TimestampMixin should set created_at on insert."""
        from datetime import datetime

        from src.models.newsletter import Newsletter

        newsletter = Newsletter(
            name="Test Newsletter",
            gmail_label_id="Label_123",
            gmail_label_name="Test Label",
        )
        async_session.add(newsletter)
        await async_session.flush()

        assert newsletter.created_at is not None
        assert isinstance(newsletter.created_at, datetime)
        # Should be recent (within last minute)
        now = datetime.now(UTC)
        assert (now - newsletter.created_at).total_seconds() < 60

    @pytest.mark.asyncio
    async def test_updated_at_default(self, async_session):
        """TimestampMixin should set updated_at on insert."""
        from datetime import datetime

        from src.models.newsletter import Newsletter

        newsletter = Newsletter(
            name="Test Newsletter",
            gmail_label_id="Label_123",
            gmail_label_name="Test Label",
        )
        async_session.add(newsletter)
        await async_session.flush()

        assert newsletter.updated_at is not None
        assert isinstance(newsletter.updated_at, datetime)
