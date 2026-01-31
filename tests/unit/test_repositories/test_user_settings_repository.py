"""Tests for UserSettingsRepository - user settings data access.

These tests verify the user settings repository correctly handles
settings storage with proper singleton pattern.
"""

from unittest.mock import patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user_settings import UserSettings
from src.repositories.user_settings_repository import UserSettingsRepository


class TestUserSettingsRepositoryGetSettings:
    """Test get_settings singleton behavior."""

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create a UserSettingsRepository."""
        return UserSettingsRepository(async_session)

    @pytest.mark.asyncio
    async def test_get_settings_creates_if_not_exists(self, repo, async_session):
        """Verify get_settings creates settings if none exist."""
        result = await repo.get_settings()
        await async_session.commit()

        assert result is not None
        assert result.id == 1

    @pytest.mark.asyncio
    async def test_get_settings_returns_existing(self, repo, async_session):
        """Verify get_settings returns existing settings."""
        # Create settings first
        first = await repo.get_settings()
        await async_session.commit()

        # Get settings again
        second = await repo.get_settings()

        assert first.id == second.id


class TestUserSettingsRepositoryLLMSettings:
    """Test LLM-related settings updates."""

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create a UserSettingsRepository."""
        return UserSettingsRepository(async_session)

    @pytest.mark.asyncio
    async def test_update_llm_enabled(self, repo, async_session):
        """Verify update_llm_enabled updates the setting."""
        await repo.get_settings()  # Ensure settings exist

        result = await repo.update_llm_enabled(True)
        await async_session.commit()

        assert result.llm_enabled is True

        # Toggle back
        result = await repo.update_llm_enabled(False)
        await async_session.commit()

        assert result.llm_enabled is False

    @pytest.mark.asyncio
    async def test_update_llm_api_base_url(self, repo, async_session):
        """Verify update_llm_api_base_url updates the setting."""
        result = await repo.update_llm_api_base_url("http://localhost:1234/v1")
        await async_session.commit()

        assert result.llm_api_base_url == "http://localhost:1234/v1"

    @pytest.mark.asyncio
    async def test_update_llm_api_base_url_to_none(self, repo, async_session):
        """Verify update_llm_api_base_url can set to None."""
        result = await repo.update_llm_api_base_url(None)
        await async_session.commit()

        assert result.llm_api_base_url is None

    @pytest.mark.asyncio
    async def test_update_llm_model(self, repo, async_session):
        """Verify update_llm_model updates the setting."""
        result = await repo.update_llm_model("gpt-4")
        await async_session.commit()

        assert result.llm_model == "gpt-4"

    @pytest.mark.asyncio
    async def test_update_llm_model_to_none(self, repo, async_session):
        """Verify update_llm_model can set to None."""
        result = await repo.update_llm_model(None)
        await async_session.commit()

        assert result.llm_model is None

    @pytest.mark.asyncio
    async def test_update_llm_max_tokens(self, repo, async_session):
        """Verify update_llm_max_tokens updates the setting."""
        result = await repo.update_llm_max_tokens(1000)
        await async_session.commit()

        assert result.llm_max_tokens == 1000

    @pytest.mark.asyncio
    async def test_update_llm_temperature(self, repo, async_session):
        """Verify update_llm_temperature updates the setting."""
        result = await repo.update_llm_temperature(0.7)
        await async_session.commit()

        assert result.llm_temperature == 0.7

    @pytest.mark.asyncio
    async def test_update_llm_temperature_clamped_min(self, repo, async_session):
        """Verify update_llm_temperature clamps to min 0."""
        result = await repo.update_llm_temperature(-0.5)
        await async_session.commit()

        assert result.llm_temperature == 0.0

    @pytest.mark.asyncio
    async def test_update_llm_temperature_clamped_max(self, repo, async_session):
        """Verify update_llm_temperature clamps to max 1."""
        result = await repo.update_llm_temperature(1.5)
        await async_session.commit()

        assert result.llm_temperature == 1.0


class TestUserSettingsRepositoryApiKey:
    """Test API key encryption."""

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create a UserSettingsRepository."""
        return UserSettingsRepository(async_session)

    @pytest.mark.asyncio
    async def test_update_llm_api_key_encrypts(self, repo, async_session):
        """Verify update_llm_api_key encrypts the key."""
        with patch("src.repositories.user_settings_repository.encrypt_value") as mock_encrypt:
            mock_encrypt.return_value = "encrypted_key"

            result = await repo.update_llm_api_key("plain_key")
            await async_session.commit()

            mock_encrypt.assert_called_once_with("plain_key")
            assert result.llm_api_key_encrypted == "encrypted_key"

    @pytest.mark.asyncio
    async def test_update_llm_api_key_to_none(self, repo, async_session):
        """Verify update_llm_api_key can set to None."""
        result = await repo.update_llm_api_key(None)
        await async_session.commit()

        assert result.llm_api_key_encrypted is None


class TestUserSettingsRepositoryTheme:
    """Test theme settings."""

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create a UserSettingsRepository."""
        return UserSettingsRepository(async_session)

    @pytest.mark.asyncio
    async def test_update_active_theme(self, repo, async_session):
        """Verify update_active_theme updates the setting."""
        result = await repo.update_active_theme("dark_slate.json")
        await async_session.commit()

        assert result.active_theme == "dark_slate.json"

    @pytest.mark.asyncio
    async def test_update_active_theme_to_none_uses_default(self, repo, async_session):
        """Verify update_active_theme uses default.json when None."""
        result = await repo.update_active_theme(None)
        await async_session.commit()

        assert result.active_theme == "default.json"


class TestUserSettingsRepositoryInheritance:
    """Test that repository inherits base operations."""

    @pytest_asyncio.fixture
    async def repo(self, async_session: AsyncSession):
        """Create a UserSettingsRepository."""
        return UserSettingsRepository(async_session)

    @pytest.mark.asyncio
    async def test_get_by_id(self, repo, async_session):
        """Verify inherited get_by_id works."""
        # Create settings first
        settings = await repo.get_settings()
        await async_session.commit()

        # Use inherited get_by_id
        result = await repo.get_by_id(1)

        assert result is not None
        assert result.id == 1

    @pytest.mark.asyncio
    async def test_exists(self, repo, async_session):
        """Verify inherited exists works."""
        # Create settings
        await repo.get_settings()
        await async_session.commit()

        result = await repo.exists(1)

        assert result is True

    @pytest.mark.asyncio
    async def test_count(self, repo, async_session):
        """Verify inherited count works."""
        # Create settings
        await repo.get_settings()
        await async_session.commit()

        result = await repo.count()

        assert result == 1
