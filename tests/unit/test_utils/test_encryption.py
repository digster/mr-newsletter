"""Tests for encryption utilities.

These tests verify the Fernet-based encryption used for OAuth token storage.
The encryption module is security-critical as it protects user credentials.
"""

import pytest
from unittest.mock import patch, MagicMock
from cryptography.fernet import InvalidToken


class TestEncryption:
    """Test suite for encryption utility functions."""

    @pytest.fixture
    def mock_settings(self):
        """Create a mock settings object with a test encryption key."""
        mock = MagicMock()
        mock.encryption_key = "test-encryption-key-for-unit-tests-32bytes!"
        return mock

    @pytest.fixture
    def encryption_module(self, mock_settings):
        """Import encryption module with mocked settings."""
        with patch("src.utils.encryption.get_settings", return_value=mock_settings):
            # Clear any cached Fernet instance
            from src.utils import encryption
            # Re-import to ensure we get fresh functions
            import importlib
            importlib.reload(encryption)
            yield encryption

    def test_encrypt_value_returns_string(self, encryption_module):
        """Verify encrypt_value returns a string type."""
        result = encryption_module.encrypt_value("test plaintext")
        assert isinstance(result, str)

    def test_encrypt_value_is_not_plaintext(self, encryption_module):
        """Verify encrypted value differs from original plaintext."""
        plaintext = "sensitive oauth token"
        encrypted = encryption_module.encrypt_value(plaintext)

        assert encrypted != plaintext
        assert "sensitive" not in encrypted
        assert "oauth" not in encrypted
        assert "token" not in encrypted

    def test_decrypt_value_recovers_plaintext(self, encryption_module):
        """Verify decryption recovers the original plaintext."""
        plaintext = "my secret access token"
        encrypted = encryption_module.encrypt_value(plaintext)
        decrypted = encryption_module.decrypt_value(encrypted)

        assert decrypted == plaintext

    def test_encrypt_decrypt_roundtrip_with_unicode(self, encryption_module):
        """Verify encryption/decryption works with Unicode characters."""
        plaintext = "Token with unicode: café résumé 日本語 emoji 🔐"
        encrypted = encryption_module.encrypt_value(plaintext)
        decrypted = encryption_module.decrypt_value(encrypted)

        assert decrypted == plaintext

    def test_encrypt_different_each_time(self, encryption_module):
        """Verify encryption produces different ciphertext each time (nonce uniqueness).

        This is crucial for security - Fernet uses a random nonce for each
        encryption operation, so the same plaintext produces different ciphertext.
        """
        plaintext = "same input every time"

        encrypted1 = encryption_module.encrypt_value(plaintext)
        encrypted2 = encryption_module.encrypt_value(plaintext)
        encrypted3 = encryption_module.encrypt_value(plaintext)

        # All should be different
        assert encrypted1 != encrypted2
        assert encrypted2 != encrypted3
        assert encrypted1 != encrypted3

        # But all should decrypt to the same value
        assert encryption_module.decrypt_value(encrypted1) == plaintext
        assert encryption_module.decrypt_value(encrypted2) == plaintext
        assert encryption_module.decrypt_value(encrypted3) == plaintext

    def test_encrypt_empty_string(self, encryption_module):
        """Verify empty string encryption is handled correctly."""
        plaintext = ""
        encrypted = encryption_module.encrypt_value(plaintext)
        decrypted = encryption_module.decrypt_value(encrypted)

        assert decrypted == plaintext

    def test_decrypt_invalid_ciphertext_raises(self, encryption_module):
        """Verify decrypting invalid ciphertext raises an error."""
        invalid_ciphertext = "not-a-valid-encrypted-value"

        with pytest.raises(Exception):  # Fernet raises InvalidToken
            encryption_module.decrypt_value(invalid_ciphertext)

    def test_decrypt_tampered_ciphertext_raises(self, encryption_module):
        """Verify decrypting tampered ciphertext raises an error.

        This tests that the authentication tag in Fernet catches tampering.
        """
        plaintext = "original value"
        encrypted = encryption_module.encrypt_value(plaintext)

        # Tamper with the ciphertext by modifying a character
        tampered = encrypted[:-5] + "XXXXX"

        with pytest.raises(Exception):
            encryption_module.decrypt_value(tampered)

    def test_key_derivation_consistency(self, mock_settings):
        """Verify same encryption key produces same Fernet key consistently.

        This ensures that encrypted data can be decrypted across app restarts
        as long as the encryption key setting remains the same.
        """
        with patch("src.utils.encryption.get_settings", return_value=mock_settings):
            from src.utils import encryption
            import importlib
            importlib.reload(encryption)

            # Get Fernet instance twice
            fernet1 = encryption._get_fernet()
            fernet2 = encryption._get_fernet()

            # Encrypt with first, decrypt with second
            plaintext = "cross-instance test"
            encrypted = fernet1.encrypt(plaintext.encode()).decode()
            decrypted = fernet2.decrypt(encrypted.encode()).decode()

            assert decrypted == plaintext

    def test_encrypt_long_value(self, encryption_module):
        """Verify encryption works for long values like OAuth tokens."""
        # OAuth tokens can be quite long
        long_token = "ya29." + "a" * 1000 + ".Xx" * 100
        encrypted = encryption_module.encrypt_value(long_token)
        decrypted = encryption_module.decrypt_value(encrypted)

        assert decrypted == long_token

    def test_encrypt_special_characters(self, encryption_module):
        """Verify encryption handles special characters in tokens."""
        special_chars = "token/with+special=chars&symbols!@#$%^&*(){}[]|\\:\";<>?,./`~"
        encrypted = encryption_module.encrypt_value(special_chars)
        decrypted = encryption_module.decrypt_value(encrypted)

        assert decrypted == special_chars

    def test_encrypted_value_is_base64(self, encryption_module):
        """Verify encrypted value is valid base64 (Fernet format)."""
        import base64

        plaintext = "test value"
        encrypted = encryption_module.encrypt_value(plaintext)

        # Fernet tokens are URL-safe base64 encoded
        try:
            decoded = base64.urlsafe_b64decode(encrypted)
            assert len(decoded) > 0
        except Exception as e:
            pytest.fail(f"Encrypted value is not valid base64: {e}")


class TestEncryptionWithDifferentKeys:
    """Test encryption behavior with different keys."""

    def test_different_keys_produce_different_ciphertext(self):
        """Verify different encryption keys produce different ciphertext."""
        mock_settings1 = MagicMock()
        mock_settings1.encryption_key = "first-encryption-key-32bytes!!!"

        mock_settings2 = MagicMock()
        mock_settings2.encryption_key = "second-encryption-key-32bytes!!"

        plaintext = "same plaintext"

        with patch("src.utils.encryption.get_settings", return_value=mock_settings1):
            from src.utils import encryption
            import importlib
            importlib.reload(encryption)
            encrypted1 = encryption.encrypt_value(plaintext)

        with patch("src.utils.encryption.get_settings", return_value=mock_settings2):
            importlib.reload(encryption)
            encrypted2 = encryption.encrypt_value(plaintext)

        # Different keys should produce different ciphertext
        assert encrypted1 != encrypted2

    def test_decrypt_with_wrong_key_fails(self):
        """Verify decryption fails when using a different key.

        This test verifies the fundamental security property that data encrypted
        with one key cannot be decrypted with a different key.
        """
        import base64
        import hashlib
        from cryptography.fernet import Fernet, InvalidToken

        # Create two different Fernet instances with different keys
        key1 = "original-encryption-key-32bytes!"
        key2 = "different-encryption-key-32bytes"

        # Derive Fernet keys the same way the module does
        key1_bytes = hashlib.sha256(key1.encode()).digest()
        key2_bytes = hashlib.sha256(key2.encode()).digest()

        fernet1 = Fernet(base64.urlsafe_b64encode(key1_bytes))
        fernet2 = Fernet(base64.urlsafe_b64encode(key2_bytes))

        # Encrypt with first key
        encrypted = fernet1.encrypt(b"secret data").decode()

        # Try to decrypt with second key - should fail
        with pytest.raises(InvalidToken):
            fernet2.decrypt(encrypted.encode())
