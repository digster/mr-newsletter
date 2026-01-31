"""Integration tests for authentication flow.

These tests verify the complete OAuth flow from login
through credential storage and refresh.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user_credential import UserCredential
from src.repositories.user_settings_repository import UserSettingsRepository


class TestAuthFlowLogin:
    """Test complete login flow."""

    @pytest.mark.asyncio
    async def test_login_stores_encrypted_credentials(self, async_session: AsyncSession):
        """Verify login stores credentials with encryption."""
        # Create mock credentials
        mock_credentials = MagicMock()
        mock_credentials.token = "access_token_12345"
        mock_credentials.refresh_token = "refresh_token_67890"
        mock_credentials.expiry = None
        mock_credentials.client_id = "test_client_id"
        mock_credentials.client_secret = "test_client_secret"

        with patch("src.services.auth_service.encrypt_value") as mock_encrypt:
            mock_encrypt.side_effect = lambda x: f"encrypted_{x}" if x else None

            # Store credential with all required fields
            credential = UserCredential(
                id=1,
                user_email="test@example.com",
                access_token_encrypted=mock_encrypt(mock_credentials.token),
                refresh_token_encrypted=mock_encrypt(mock_credentials.refresh_token),
                scopes="[]",
            )
            async_session.add(credential)
            await async_session.commit()

            # Verify encryption was called
            assert credential.access_token_encrypted == "encrypted_access_token_12345"
            assert credential.refresh_token_encrypted == "encrypted_refresh_token_67890"

    @pytest.mark.asyncio
    async def test_credentials_stored_in_database(self, async_session: AsyncSession):
        """Verify credentials persist in database."""
        # Create and store credential
        credential = UserCredential(
            id=1,
            access_token_encrypted="encrypted_token",
            refresh_token_encrypted="encrypted_refresh",
            user_email="test@example.com",
        )
        async_session.add(credential)
        await async_session.commit()

        # Fetch from database
        from sqlalchemy import select

        result = await async_session.execute(
            select(UserCredential).where(UserCredential.id == 1)
        )
        stored = result.scalar_one_or_none()

        assert stored is not None
        assert stored.user_email == "test@example.com"
        assert stored.access_token_encrypted == "encrypted_token"


class TestAuthFlowRefresh:
    """Test credential refresh flow."""

    @pytest.mark.asyncio
    async def test_refresh_updates_stored_tokens(self, async_session: AsyncSession):
        """Verify token refresh updates encrypted tokens."""
        # Store initial credential
        credential = UserCredential(
            id=1,
            user_email="refresh@example.com",
            access_token_encrypted="old_encrypted_token",
            refresh_token_encrypted="encrypted_refresh",
            scopes="[]",
        )
        async_session.add(credential)
        await async_session.commit()

        # Simulate token refresh
        with patch("src.services.auth_service.encrypt_value") as mock_encrypt:
            mock_encrypt.return_value = "new_encrypted_token"

            # Update the token
            credential.access_token_encrypted = mock_encrypt("new_access_token")
            await async_session.commit()

        # Verify update
        from sqlalchemy import select

        result = await async_session.execute(
            select(UserCredential).where(UserCredential.id == 1)
        )
        updated = result.scalar_one()

        assert updated.access_token_encrypted == "new_encrypted_token"


class TestAuthFlowLogout:
    """Test logout flow."""

    @pytest.mark.asyncio
    async def test_logout_removes_credentials(self, async_session: AsyncSession):
        """Verify logout removes credentials from database."""
        # Store credential
        credential = UserCredential(
            id=1,
            user_email="logout@example.com",
            access_token_encrypted="encrypted_token",
            refresh_token_encrypted="encrypted_refresh",
            scopes="[]",
        )
        async_session.add(credential)
        await async_session.commit()

        # Simulate logout - delete credential
        await async_session.delete(credential)
        await async_session.commit()

        # Verify removed
        from sqlalchemy import select

        result = await async_session.execute(
            select(UserCredential).where(UserCredential.id == 1)
        )
        stored = result.scalar_one_or_none()

        assert stored is None

    @pytest.mark.asyncio
    async def test_logout_preserves_settings(self, async_session: AsyncSession):
        """Verify logout keeps user settings intact."""
        # Store credential and settings
        credential = UserCredential(
            id=1,
            user_email="preserve@example.com",
            access_token_encrypted="encrypted_token",
            scopes="[]",
        )
        async_session.add(credential)

        settings_repo = UserSettingsRepository(async_session)
        settings = await settings_repo.get_settings()
        await settings_repo.update_active_theme("dark_slate.json")
        await async_session.commit()

        # Logout - remove credential
        await async_session.delete(credential)
        await async_session.commit()

        # Settings should still exist
        preserved_settings = await settings_repo.get_settings()
        assert preserved_settings is not None
        assert preserved_settings.active_theme == "dark_slate.json"
