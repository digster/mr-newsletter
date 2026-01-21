"""Authentication service for Gmail OAuth."""

import json
import logging
from dataclasses import dataclass
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.app_credentials import get_app_credentials, is_app_configured
from src.config.settings import get_settings
from src.models.user_credential import UserCredential
from src.utils.encryption import decrypt_value, encrypt_value

logger = logging.getLogger(__name__)

# Gmail API Scopes
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.labels",
]


@dataclass
class AuthResult:
    """Result of authentication operation."""

    success: bool
    credentials: Optional[Credentials] = None
    error: Optional[str] = None
    user_email: Optional[str] = None


class AuthService:
    """Service for handling Gmail OAuth authentication.

    All credentials are stored encrypted in PostgreSQL.
    """

    def __init__(self, session: AsyncSession):
        """Initialize auth service.

        Args:
            session: Async database session.
        """
        self.session = session
        self._credentials: Optional[Credentials] = None

    async def is_app_configured(self) -> bool:
        """Check if app OAuth credentials are configured.

        Checks for credentials from bundled encrypted file (desktop)
        or environment variables (web/development).

        Returns:
            True if configured, False otherwise.
        """
        return is_app_configured()

    def get_app_credentials(self) -> Optional[tuple[str, str]]:
        """Get app credentials from bundled file or environment variables.

        Returns:
            Tuple of (client_id, client_secret) or None.
        """
        return get_app_credentials()

    async def get_user_credentials(
        self,
        user_email: Optional[str] = None,
    ) -> AuthResult:
        """Get valid user credentials, refreshing if needed.

        Args:
            user_email: User email to get credentials for. If None, gets first user.

        Returns:
            AuthResult with credentials if successful.
        """
        # Load from database
        creds = await self._load_user_credentials(user_email)

        if creds and creds.valid:
            self._credentials = creds
            return AuthResult(
                success=True,
                credentials=creds,
                user_email=user_email,
            )

        # Try to refresh if expired
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Save refreshed token
                await self._save_user_credentials(user_email or "", creds)
                self._credentials = creds
                return AuthResult(
                    success=True,
                    credentials=creds,
                    user_email=user_email,
                )
            except Exception as e:
                logger.warning(f"Token refresh failed: {e}")

        # Need new authentication
        return AuthResult(
            success=False,
            error="Authentication required",
        )

    async def start_oauth_flow(self, port: int = 0) -> AuthResult:
        """Start OAuth flow for new authentication.

        Args:
            port: Local port for OAuth callback (0 = random).

        Returns:
            AuthResult with credentials if successful.
        """
        app_creds = self.get_app_credentials()
        if not app_creds:
            return AuthResult(
                success=False,
                error="App credentials not configured. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables.",
            )

        client_id, client_secret = app_creds

        try:
            # Create client config for InstalledAppFlow
            client_config = {
                "installed": {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost"],
                }
            }

            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)

            # Run local server for OAuth callback
            creds = flow.run_local_server(port=port)

            # Get user email from credentials
            user_email = self._get_email_from_credentials(creds)

            # Save credentials
            await self._save_user_credentials(user_email, creds)

            self._credentials = creds
            logger.info(f"OAuth completed for user: {user_email}")

            return AuthResult(
                success=True,
                credentials=creds,
                user_email=user_email,
            )
        except Exception as e:
            logger.error(f"OAuth flow failed: {e}")
            return AuthResult(
                success=False,
                error=str(e),
            )

    def _get_email_from_credentials(self, creds: Credentials) -> str:
        """Extract email from credentials.

        This requires making an API call to get user info.
        For simplicity, we'll use a placeholder until we can make the API call.
        """
        # The email will be set properly when we make the first Gmail API call
        return "user@gmail.com"

    async def _load_user_credentials(
        self,
        user_email: Optional[str] = None,
    ) -> Optional[Credentials]:
        """Load user credentials from database.

        Args:
            user_email: User email. If None, loads first user.

        Returns:
            Credentials if found, None otherwise.
        """
        if user_email:
            query = select(UserCredential).where(
                UserCredential.user_email == user_email
            )
        else:
            query = select(UserCredential).limit(1)

        result = await self.session.execute(query)
        user_cred = result.scalar_one_or_none()

        if not user_cred:
            return None

        try:
            access_token = decrypt_value(user_cred.access_token_encrypted)
            refresh_token = None
            if user_cred.refresh_token_encrypted:
                refresh_token = decrypt_value(user_cred.refresh_token_encrypted)

            # Get app credentials for client_id and client_secret
            app_creds = self.get_app_credentials()
            if not app_creds:
                return None

            client_id, client_secret = app_creds
            scopes = json.loads(user_cred.scopes)

            # Ensure expiry is timezone-naive (google-auth uses naive UTC datetimes)
            expiry = user_cred.token_expiry
            if expiry is not None and expiry.tzinfo is not None:
                expiry = expiry.replace(tzinfo=None)

            creds = Credentials(
                token=access_token,
                refresh_token=refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=client_id,
                client_secret=client_secret,
                scopes=scopes,
                expiry=expiry,
            )

            return creds
        except Exception as e:
            logger.error(
                f"Failed to load user credentials ({type(e).__name__}): {e}",
                exc_info=True
            )
            # If decryption fails, the stored credentials are unusable
            # (likely encrypted with a different key). Clear them so user can re-auth.
            if user_cred:
                try:
                    await self.session.delete(user_cred)
                    await self.session.commit()
                    logger.warning(
                        "Cleared unusable credentials - user will need to re-authenticate"
                    )
                except Exception as cleanup_error:
                    logger.error(f"Failed to clear unusable credentials: {cleanup_error}")
            return None

    async def _save_user_credentials(
        self,
        user_email: str,
        creds: Credentials,
    ) -> None:
        """Save user credentials to database.

        Args:
            user_email: User email.
            creds: OAuth credentials.
        """
        try:
            encrypted_access = encrypt_value(creds.token)
            encrypted_refresh = None
            if creds.refresh_token:
                encrypted_refresh = encrypt_value(creds.refresh_token)

            scopes_json = json.dumps(list(creds.scopes or []))

            # Check if exists
            result = await self.session.execute(
                select(UserCredential).where(UserCredential.user_email == user_email)
            )
            user_cred = result.scalar_one_or_none()

            if user_cred:
                # Update existing
                user_cred.access_token_encrypted = encrypted_access
                if encrypted_refresh:
                    user_cred.refresh_token_encrypted = encrypted_refresh
                user_cred.token_expiry = creds.expiry
                user_cred.scopes = scopes_json
            else:
                # Create new
                user_cred = UserCredential(
                    user_email=user_email,
                    access_token_encrypted=encrypted_access,
                    refresh_token_encrypted=encrypted_refresh,
                    token_expiry=creds.expiry,
                    scopes=scopes_json,
                )
                self.session.add(user_cred)

            await self.session.commit()
        except Exception as e:
            logger.error(f"Failed to save user credentials: {e}")
            await self.session.rollback()

    async def logout(self, user_email: Optional[str] = None) -> bool:
        """Clear stored user credentials.

        Args:
            user_email: User email to logout. If None, clears all.

        Returns:
            True if successful.
        """
        try:
            if user_email:
                result = await self.session.execute(
                    select(UserCredential).where(
                        UserCredential.user_email == user_email
                    )
                )
                user_cred = result.scalar_one_or_none()
                if user_cred:
                    await self.session.delete(user_cred)
            else:
                # Delete all user credentials
                result = await self.session.execute(select(UserCredential))
                for user_cred in result.scalars():
                    await self.session.delete(user_cred)

            await self.session.commit()
            self._credentials = None
            return True
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            await self.session.rollback()
            return False

    async def get_current_user_email(self) -> Optional[str]:
        """Get current logged in user email.

        Returns:
            User email or None.
        """
        result = await self.session.execute(select(UserCredential).limit(1))
        user_cred = result.scalar_one_or_none()
        return user_cred.user_email if user_cred else None

    async def update_user_email(self, old_email: str, new_email: str) -> bool:
        """Update user email after OAuth when we get the real email.

        Args:
            old_email: Placeholder email.
            new_email: Real email from Gmail API.

        Returns:
            True if updated.
        """
        if old_email == new_email:
            return True

        try:
            # Get the placeholder record
            result = await self.session.execute(
                select(UserCredential).where(UserCredential.user_email == old_email)
            )
            placeholder_cred = result.scalar_one_or_none()

            if not placeholder_cred:
                return False

            # Check if the new email already exists
            result = await self.session.execute(
                select(UserCredential).where(UserCredential.user_email == new_email)
            )
            existing_cred = result.scalar_one_or_none()

            if existing_cred:
                # Transfer fresh credentials to existing record
                existing_cred.access_token_encrypted = placeholder_cred.access_token_encrypted
                existing_cred.refresh_token_encrypted = placeholder_cred.refresh_token_encrypted
                existing_cred.token_expiry = placeholder_cred.token_expiry
                existing_cred.scopes = placeholder_cred.scopes
                # Delete placeholder record
                await self.session.delete(placeholder_cred)
            else:
                # Simply update the email
                placeholder_cred.user_email = new_email

            await self.session.commit()
            return True
        except Exception as e:
            logger.error(f"Failed to update user email: {e}")
            await self.session.rollback()
            return False
