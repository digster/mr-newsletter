"""Encryption utilities for securing credentials in the database."""

import base64
import hashlib

from cryptography.fernet import Fernet

from src.config.settings import get_settings


def _get_fernet() -> Fernet:
    """Get Fernet instance with key derived from settings."""
    settings = get_settings()
    # Derive a 32-byte key from the encryption key using SHA-256
    key_bytes = hashlib.sha256(settings.encryption_key.encode()).digest()
    # Fernet requires a URL-safe base64-encoded 32-byte key
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(fernet_key)


def encrypt_value(plaintext: str) -> str:
    """Encrypt a string value.

    Args:
        plaintext: The string to encrypt.

    Returns:
        Base64-encoded encrypted string.
    """
    fernet = _get_fernet()
    encrypted = fernet.encrypt(plaintext.encode())
    return encrypted.decode()


def decrypt_value(ciphertext: str) -> str:
    """Decrypt an encrypted string value.

    Args:
        ciphertext: The base64-encoded encrypted string.

    Returns:
        Decrypted plaintext string.
    """
    fernet = _get_fernet()
    decrypted = fernet.decrypt(ciphertext.encode())
    return decrypted.decode()
