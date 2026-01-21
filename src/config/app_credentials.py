"""App credentials loader for OAuth client ID and secret.

This module provides a unified way to load OAuth credentials:
- Desktop mode: Tries to load from encrypted bundled .appdata file first
- Web mode / fallback: Uses environment variables via Pydantic Settings

The .appdata file is generated at build time by scripts/generate_app_config.py
and bundled into the .app by PyInstaller.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Optional

from src.config.settings import get_settings
from src.utils.encryption import decrypt_value

logger = logging.getLogger(__name__)


def _get_bundled_config_path() -> Path:
    """Get the path to the bundled config file.

    In a PyInstaller bundle on macOS:
    - For .app bundles: data files are in Contents/Resources/
    - For other bundles: data files are in sys._MEIPASS

    In development, use the source directory.
    """
    # Check if running as a PyInstaller bundle
    if getattr(sys, 'frozen', False):
        # Get the executable path
        executable_path = Path(sys.executable)

        # Check if we're in a macOS .app bundle (path contains .app/Contents/MacOS/)
        if ".app/Contents/MacOS" in str(executable_path):
            # Navigate from Contents/MacOS/exe -> Contents/Resources/
            resources_path = executable_path.parent.parent / "Resources"
            config_path = resources_path / "src" / "config" / ".appdata"
            logger.debug(f"macOS app bundle detected, checking: {config_path}")
            if config_path.exists():
                return config_path

        # Fallback: try sys._MEIPASS (standard PyInstaller location)
        if hasattr(sys, '_MEIPASS'):
            base_path = Path(sys._MEIPASS)
            config_path = base_path / "src" / "config" / ".appdata"
            logger.debug(f"Checking _MEIPASS location: {config_path}")
            return config_path

    # Running in development - use source directory
    return Path(__file__).parent / ".appdata"


def _load_from_bundled_file() -> Optional[tuple[str, str]]:
    """Load credentials from encrypted bundled file.

    Returns:
        Tuple of (client_id, client_secret) or None if file doesn't exist.
    """
    config_path = _get_bundled_config_path()
    logger.info(f"Looking for bundled config at: {config_path}")

    if not config_path.exists():
        logger.info(f"Bundled config not found at: {config_path}")
        return None

    try:
        logger.info(f"Found bundled config, attempting to decrypt...")
        # Read encrypted data
        encrypted_data = config_path.read_text()

        # Decrypt using the same mechanism as user tokens
        decrypted_json = decrypt_value(encrypted_data)
        config = json.loads(decrypted_json)

        client_id = config.get("client_id", "")
        client_secret = config.get("client_secret", "")

        if client_id and client_secret:
            logger.info("Successfully loaded app credentials from bundled config")
            return (client_id, client_secret)

        logger.warning("Bundled config exists but missing credentials")
        return None

    except Exception as e:
        logger.error(f"Failed to load bundled config: {e}", exc_info=True)
        return None


def get_app_credentials() -> Optional[tuple[str, str]]:
    """Load app credentials from encrypted bundled file or environment variables.

    In desktop mode, tries the bundled encrypted file first (for distribution),
    then falls back to environment variables (for development).

    In web mode, always uses environment variables.

    Returns:
        Tuple of (client_id, client_secret) or None if not configured.
    """
    settings = get_settings()

    # Desktop mode: try bundled encrypted file first
    if settings.is_desktop_mode:
        bundled_creds = _load_from_bundled_file()
        if bundled_creds:
            return bundled_creds
        logger.debug("Falling back to environment variables for credentials")

    # Web mode or fallback: use environment variables
    if settings.is_oauth_configured:
        return (settings.google_client_id, settings.google_client_secret)

    return None


def is_app_configured() -> bool:
    """Check if app OAuth credentials are available from any source.

    Returns:
        True if credentials are available, False otherwise.
    """
    return get_app_credentials() is not None
