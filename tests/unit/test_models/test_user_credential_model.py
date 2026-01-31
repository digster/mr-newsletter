"""Tests for UserCredential model.

These tests verify the UserCredential model's field constraints
and encrypted token storage.
"""

from datetime import datetime, timezone

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from src.models.user_credential import UserCredential


class TestUserCredentialModelCreation:
    """Test UserCredential model creation."""

    @pytest.mark.asyncio
    async def test_create_credential_with_required_fields(
        self, async_session: AsyncSession
    ):
        """Verify credential can be created with minimum required fields."""
        credential = UserCredential(
            user_email="test@example.com",
            access_token_encrypted="encrypted_access_token",
            scopes="[]",
        )
        async_session.add(credential)
        await async_session.commit()

        assert credential.id is not None
        assert credential.user_email == "test@example.com"
        assert credential.access_token_encrypted == "encrypted_access_token"

    @pytest.mark.asyncio
    async def test_create_credential_with_all_fields(
        self, async_session: AsyncSession
    ):
        """Verify credential can be created with all fields."""
        expiry = datetime.now(timezone.utc)
        credential = UserCredential(
            user_email="full@example.com",
            access_token_encrypted="encrypted_access",
            refresh_token_encrypted="encrypted_refresh",
            token_expiry=expiry,
            scopes='["https://www.googleapis.com/auth/gmail.readonly"]',
        )
        async_session.add(credential)
        await async_session.commit()

        assert credential.refresh_token_encrypted == "encrypted_refresh"
        assert credential.token_expiry is not None
        assert "gmail.readonly" in credential.scopes


class TestUserCredentialModelConstraints:
    """Test UserCredential model constraints."""

    @pytest.mark.asyncio
    async def test_unique_user_email_constraint(self, async_session: AsyncSession):
        """Verify user_email must be unique."""
        credential1 = UserCredential(
            user_email="unique@example.com",
            access_token_encrypted="token1",
            scopes="[]",
        )
        async_session.add(credential1)
        await async_session.commit()

        credential2 = UserCredential(
            user_email="unique@example.com",  # Same email
            access_token_encrypted="token2",
            scopes="[]",
        )
        async_session.add(credential2)

        with pytest.raises(IntegrityError):
            await async_session.commit()

    @pytest.mark.asyncio
    async def test_user_email_required(self, async_session: AsyncSession):
        """Verify user_email is required."""
        credential = UserCredential(
            user_email=None,  # type: ignore
            access_token_encrypted="token",
            scopes="[]",
        )
        async_session.add(credential)

        with pytest.raises(IntegrityError):
            await async_session.commit()

    @pytest.mark.asyncio
    async def test_access_token_required(self, async_session: AsyncSession):
        """Verify access_token_encrypted is required."""
        credential = UserCredential(
            user_email="notoken@example.com",
            access_token_encrypted=None,  # type: ignore
            scopes="[]",
        )
        async_session.add(credential)

        with pytest.raises(IntegrityError):
            await async_session.commit()


class TestUserCredentialEncryptedFields:
    """Test encrypted field storage."""

    @pytest.mark.asyncio
    async def test_encrypted_fields_store_as_text(self, async_session: AsyncSession):
        """Verify encrypted tokens are stored as text."""
        # Simulated encrypted values (in real app, these would be Fernet ciphertext)
        encrypted_access = "gAAAAABhL..." * 10  # Long encrypted string
        encrypted_refresh = "gAAAAABhM..." * 10

        credential = UserCredential(
            user_email="encrypted@example.com",
            access_token_encrypted=encrypted_access,
            refresh_token_encrypted=encrypted_refresh,
            scopes="[]",
        )
        async_session.add(credential)
        await async_session.commit()

        # Fetch and verify stored correctly
        from sqlalchemy import select

        result = await async_session.execute(
            select(UserCredential).where(
                UserCredential.user_email == "encrypted@example.com"
            )
        )
        stored = result.scalar_one()

        assert stored.access_token_encrypted == encrypted_access
        assert stored.refresh_token_encrypted == encrypted_refresh

    @pytest.mark.asyncio
    async def test_refresh_token_is_optional(self, async_session: AsyncSession):
        """Verify refresh_token_encrypted is optional."""
        credential = UserCredential(
            user_email="norefresh@example.com",
            access_token_encrypted="token",
            refresh_token_encrypted=None,  # No refresh token
            scopes="[]",
        )
        async_session.add(credential)
        await async_session.commit()

        assert credential.refresh_token_encrypted is None


class TestUserCredentialTokenExpiry:
    """Test token expiry handling."""

    @pytest.mark.asyncio
    async def test_token_expiry_optional(self, async_session: AsyncSession):
        """Verify token_expiry is optional."""
        credential = UserCredential(
            user_email="noexpiry@example.com",
            access_token_encrypted="token",
            token_expiry=None,
            scopes="[]",
        )
        async_session.add(credential)
        await async_session.commit()

        assert credential.token_expiry is None

    @pytest.mark.asyncio
    async def test_token_expiry_stores_datetime(self, async_session: AsyncSession):
        """Verify token_expiry stores datetime correctly."""
        expiry = datetime(2025, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
        credential = UserCredential(
            user_email="withexpiry@example.com",
            access_token_encrypted="token",
            token_expiry=expiry,
            scopes="[]",
        )
        async_session.add(credential)
        await async_session.commit()

        assert credential.token_expiry == expiry


class TestUserCredentialRepr:
    """Test UserCredential model string representation."""

    @pytest.mark.asyncio
    async def test_credential_repr(self, async_session: AsyncSession):
        """Verify credential __repr__ format."""
        credential = UserCredential(
            user_email="repr@example.com",
            access_token_encrypted="token",
            scopes="[]",
        )
        async_session.add(credential)
        await async_session.commit()

        repr_str = repr(credential)
        assert "UserCredential" in repr_str
        assert "repr@example.com" in repr_str
