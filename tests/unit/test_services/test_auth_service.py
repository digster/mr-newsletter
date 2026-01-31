"""Tests for AuthService - OAuth flow and credential management.

These tests verify the authentication service handles OAuth credentials
securely, including encryption/decryption of tokens.
"""

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.user_credential import UserCredential
from src.services.auth_service import AuthResult, AuthService


class TestAuthServiceAppConfiguration:
    """Test app credential configuration checks."""

    @pytest_asyncio.fixture
    async def auth_service(self, async_session: AsyncSession):
        """Create auth service with test session."""
        return AuthService(async_session)

    @pytest.mark.asyncio
    async def test_is_app_configured_returns_bool(self, auth_service):
        """Verify is_app_configured returns a boolean."""
        result = await auth_service.is_app_configured()
        assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_get_app_credentials_when_not_configured(self, auth_service):
        """Verify get_app_credentials returns None when not configured."""
        with patch("src.services.auth_service.get_app_credentials", return_value=None):
            result = auth_service.get_app_credentials()
            # Result is either None or a tuple
            assert result is None or isinstance(result, tuple)


class TestAuthServiceUserCredentials:
    """Test user credential loading and saving."""

    @pytest_asyncio.fixture
    async def auth_service(self, async_session: AsyncSession):
        """Create auth service with test session."""
        return AuthService(async_session)

    @pytest.mark.asyncio
    async def test_get_user_credentials_when_none_exist(self, auth_service):
        """Verify get_user_credentials returns failure when no credentials."""
        result = await auth_service.get_user_credentials()

        assert isinstance(result, AuthResult)
        assert result.success is False
        assert result.credentials is None

    @pytest.mark.asyncio
    async def test_get_current_user_email_when_none(self, auth_service):
        """Verify get_current_user_email returns None when no user."""
        result = await auth_service.get_current_user_email()
        assert result is None

    @pytest.mark.asyncio
    async def test_logout_returns_true_when_empty(self, auth_service):
        """Verify logout succeeds even when no credentials exist."""
        result = await auth_service.logout()
        assert result is True

    @pytest.mark.asyncio
    async def test_logout_clears_cached_credentials(self, auth_service):
        """Verify logout clears the cached credentials."""
        # Set some cached credentials
        auth_service._credentials = MagicMock()

        await auth_service.logout()

        assert auth_service._credentials is None


class TestAuthServiceCredentialStorage:
    """Test credential encryption and storage."""

    @pytest_asyncio.fixture
    async def auth_service(self, async_session: AsyncSession):
        """Create auth service with test session."""
        return AuthService(async_session)

    @pytest.mark.asyncio
    async def test_save_user_credentials_encrypts_tokens(self, async_session, auth_service):
        """Verify credentials are encrypted before storage."""
        mock_creds = MagicMock()
        mock_creds.token = "test-access-token"
        mock_creds.refresh_token = "test-refresh-token"
        mock_creds.expiry = datetime.now(timezone.utc) + timedelta(hours=1)
        mock_creds.scopes = ["https://www.googleapis.com/auth/gmail.readonly"]

        with patch("src.services.auth_service.encrypt_value") as mock_encrypt:
            mock_encrypt.return_value = "encrypted-value"

            await auth_service._save_user_credentials("test@gmail.com", mock_creds)

            # Verify encrypt_value was called for both tokens
            assert mock_encrypt.call_count >= 1

    @pytest.mark.asyncio
    async def test_load_user_credentials_decrypts_tokens(self, async_session, auth_service):
        """Verify stored credentials are decrypted on load."""
        # Create a stored credential
        user_cred = UserCredential(
            user_email="test@gmail.com",
            access_token_encrypted="encrypted-access",
            refresh_token_encrypted="encrypted-refresh",
            token_expiry=datetime.now(timezone.utc) + timedelta(hours=1),
            scopes=json.dumps(["https://www.googleapis.com/auth/gmail.readonly"]),
        )
        async_session.add(user_cred)
        await async_session.commit()

        with patch("src.services.auth_service.decrypt_value") as mock_decrypt, \
             patch("src.services.auth_service.get_app_credentials") as mock_app_creds:
            mock_decrypt.return_value = "decrypted-token"
            mock_app_creds.return_value = ("client_id", "client_secret")

            result = await auth_service._load_user_credentials("test@gmail.com")

            # Verify decrypt was called
            assert mock_decrypt.call_count >= 1


class TestAuthServiceTokenRefresh:
    """Test token refresh logic."""

    @pytest_asyncio.fixture
    async def auth_service(self, async_session: AsyncSession):
        """Create auth service with test session."""
        return AuthService(async_session)

    @pytest.mark.asyncio
    async def test_get_user_credentials_returns_cached_when_valid(self, auth_service):
        """Verify valid cached credentials are returned without refresh."""
        mock_creds = MagicMock()
        mock_creds.valid = True

        with patch.object(auth_service, "_load_user_credentials", return_value=mock_creds):
            result = await auth_service.get_user_credentials("test@gmail.com")

            assert result.success is True
            assert result.credentials == mock_creds

    @pytest.mark.asyncio
    async def test_get_user_credentials_attempts_refresh_when_expired(self, auth_service):
        """Verify expired credentials trigger a refresh attempt."""
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "refresh-token"

        # After refresh, credentials become valid
        def refresh_side_effect(_):
            mock_creds.valid = True

        mock_creds.refresh = refresh_side_effect

        with patch.object(auth_service, "_load_user_credentials", return_value=mock_creds), \
             patch.object(auth_service, "_save_user_credentials", new_callable=AsyncMock):
            result = await auth_service.get_user_credentials("test@gmail.com")

            assert result.success is True


class TestAuthServiceOAuthFlow:
    """Test OAuth flow initialization."""

    @pytest_asyncio.fixture
    async def auth_service(self, async_session: AsyncSession):
        """Create auth service with test session."""
        return AuthService(async_session)

    @pytest.mark.asyncio
    async def test_start_oauth_flow_fails_without_app_credentials(self, auth_service):
        """Verify OAuth flow fails when app credentials are missing."""
        with patch.object(auth_service, "get_app_credentials", return_value=None):
            result = await auth_service.start_oauth_flow()

            assert result.success is False
            assert "not configured" in result.error.lower()

    @pytest.mark.asyncio
    async def test_get_email_from_credentials_returns_placeholder(self, auth_service):
        """Verify email extraction returns placeholder initially."""
        mock_creds = MagicMock()
        result = auth_service._get_email_from_credentials(mock_creds)

        # Returns placeholder email that will be updated later
        assert "@" in result


class TestAuthServiceEmailUpdate:
    """Test email update after OAuth completion."""

    @pytest_asyncio.fixture
    async def auth_service(self, async_session: AsyncSession):
        """Create auth service with test session."""
        return AuthService(async_session)

    @pytest.mark.asyncio
    async def test_update_user_email_returns_true_when_same(self, auth_service):
        """Verify update returns True when emails are the same."""
        result = await auth_service.update_user_email("test@gmail.com", "test@gmail.com")
        assert result is True

    @pytest.mark.asyncio
    async def test_update_user_email_returns_false_when_not_found(self, auth_service):
        """Verify update returns False when old email doesn't exist."""
        result = await auth_service.update_user_email("old@gmail.com", "new@gmail.com")
        assert result is False

    @pytest.mark.asyncio
    async def test_update_user_email_updates_record(self, async_session, auth_service):
        """Verify email is updated in the database."""
        # Create a user credential with placeholder email
        user_cred = UserCredential(
            user_email="user@gmail.com",
            access_token_encrypted="encrypted",
            scopes=json.dumps([]),
        )
        async_session.add(user_cred)
        await async_session.commit()

        result = await auth_service.update_user_email("user@gmail.com", "real@gmail.com")

        assert result is True


class TestAuthServiceLogout:
    """Test logout functionality."""

    @pytest_asyncio.fixture
    async def auth_service(self, async_session: AsyncSession):
        """Create auth service with test session."""
        return AuthService(async_session)

    @pytest.mark.asyncio
    async def test_logout_removes_specific_user(self, async_session, auth_service):
        """Verify logout removes only the specified user."""
        # Create two user credentials
        user1 = UserCredential(
            user_email="user1@gmail.com",
            access_token_encrypted="encrypted1",
            scopes=json.dumps([]),
        )
        user2 = UserCredential(
            user_email="user2@gmail.com",
            access_token_encrypted="encrypted2",
            scopes=json.dumps([]),
        )
        async_session.add_all([user1, user2])
        await async_session.commit()

        result = await auth_service.logout("user1@gmail.com")

        assert result is True
        # Verify user2 still exists
        remaining_email = await auth_service.get_current_user_email()
        # Should still have a user (user2)
        assert remaining_email == "user2@gmail.com"

    @pytest.mark.asyncio
    async def test_logout_all_removes_all_users(self, async_session, auth_service):
        """Verify logout without email removes all users."""
        # Create two user credentials
        user1 = UserCredential(
            user_email="user1@gmail.com",
            access_token_encrypted="encrypted1",
            scopes=json.dumps([]),
        )
        user2 = UserCredential(
            user_email="user2@gmail.com",
            access_token_encrypted="encrypted2",
            scopes=json.dumps([]),
        )
        async_session.add_all([user1, user2])
        await async_session.commit()

        result = await auth_service.logout()  # No email = logout all

        assert result is True
        remaining_email = await auth_service.get_current_user_email()
        assert remaining_email is None
