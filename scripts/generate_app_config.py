#!/usr/bin/env python3
"""Generate encrypted app config file from environment variables.

This script reads GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET from .env
and creates an encrypted config file that gets bundled into the desktop app.

Usage:
    uv run python scripts/generate_app_config.py

The encrypted file is written to src/config/.appdata and should be
gitignored (credentials should never be in version control).
"""

import base64
import hashlib
import json
import sys
from pathlib import Path

from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os

# IMPORTANT: Use the SAME default key as src/config/settings.py (line 48)
# When the bundled .app runs from Finder, no environment variables are available,
# so settings.py falls back to this default key. We must encrypt with the same key
# that the app will use at runtime for decryption to succeed.
# This is obfuscation, not security - OAuth client credentials in desktop apps
# are not truly secret (they're embedded in the binary). User tokens remain secure.
BUNDLED_APP_ENCRYPTION_KEY = "dev-encryption-key-change-in-production"


def get_fernet(encryption_key: str) -> Fernet:
    """Get Fernet instance with key derived from encryption key.

    This matches the encryption logic in src/utils/encryption.py.
    """
    key_bytes = hashlib.sha256(encryption_key.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(fernet_key)


def main() -> int:
    """Generate encrypted app config file."""
    # Load .env file
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        print(f"ERROR: .env file not found at {env_path}")
        print("Please create a .env file with GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")
        return 1

    load_dotenv(env_path)

    # Get required values from .env
    client_id = os.getenv("GOOGLE_CLIENT_ID", "")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET", "")

    # Always use the bundled app encryption key (NOT from .env)
    # This must match the default in src/config/settings.py for runtime decryption
    encryption_key = BUNDLED_APP_ENCRYPTION_KEY

    if not client_id or not client_secret:
        print("ERROR: GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set in .env")
        return 1

    # Create config data
    config_data = {
        "client_id": client_id,
        "client_secret": client_secret,
    }

    # Encrypt the config
    fernet = get_fernet(encryption_key)
    config_json = json.dumps(config_data)
    encrypted_data = fernet.encrypt(config_json.encode())

    # Write to src/config/.appdata
    output_path = Path(__file__).parent.parent / "src" / "config" / ".appdata"
    output_path.write_bytes(encrypted_data)

    print(f"Encrypted app config written to: {output_path}")
    print("This file will be bundled into the desktop app during build.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
