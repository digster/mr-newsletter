"""User settings repository for data access."""


from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user_settings import UserSettings
from src.utils.encryption import encrypt_value

from .base_repository import BaseRepository


class UserSettingsRepository(BaseRepository[UserSettings]):
    """Repository for UserSettings entity operations."""

    def __init__(self, session: AsyncSession):
        """Initialize user settings repository.

        Args:
            session: Async database session.
        """
        super().__init__(session, UserSettings)

    async def get_settings(self) -> UserSettings:
        """Get or create user settings (singleton pattern).

        Returns:
            UserSettings instance.
        """
        result = await self.session.execute(
            select(UserSettings).where(UserSettings.id == 1)
        )
        settings = result.scalar_one_or_none()

        if not settings:
            settings = UserSettings(id=1)
            self.session.add(settings)
            await self.session.flush()

        return settings

    async def update_llm_enabled(self, enabled: bool) -> UserSettings:
        """Update LLM enabled setting.

        Args:
            enabled: Whether LLM is enabled.

        Returns:
            Updated settings.
        """
        settings = await self.get_settings()
        settings.llm_enabled = enabled
        await self.session.flush()
        return settings

    async def update_llm_api_base_url(self, url: str | None) -> UserSettings:
        """Update LLM API base URL.

        Args:
            url: API base URL.

        Returns:
            Updated settings.
        """
        settings = await self.get_settings()
        settings.llm_api_base_url = url
        await self.session.flush()
        return settings

    async def update_llm_api_key(self, api_key: str | None) -> UserSettings:
        """Update LLM API key (encrypted).

        Args:
            api_key: Plain text API key to encrypt and store.

        Returns:
            Updated settings.
        """
        settings = await self.get_settings()
        if api_key:
            settings.llm_api_key_encrypted = encrypt_value(api_key)
        else:
            settings.llm_api_key_encrypted = None
        await self.session.flush()
        return settings

    async def update_llm_model(self, model: str | None) -> UserSettings:
        """Update LLM model name.

        Args:
            model: Model name/ID.

        Returns:
            Updated settings.
        """
        settings = await self.get_settings()
        settings.llm_model = model
        await self.session.flush()
        return settings

    async def update_llm_max_tokens(self, max_tokens: int) -> UserSettings:
        """Update LLM max tokens.

        Args:
            max_tokens: Maximum tokens for responses.

        Returns:
            Updated settings.
        """
        settings = await self.get_settings()
        settings.llm_max_tokens = max_tokens
        await self.session.flush()
        return settings

    async def update_llm_temperature(self, temperature: float) -> UserSettings:
        """Update LLM temperature.

        Args:
            temperature: Temperature value (0-1).

        Returns:
            Updated settings.
        """
        settings = await self.get_settings()
        settings.llm_temperature = max(0.0, min(1.0, temperature))
        await self.session.flush()
        return settings
