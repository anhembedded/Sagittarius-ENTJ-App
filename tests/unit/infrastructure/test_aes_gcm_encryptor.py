"""Unit tests for AES-GCM encryptor."""

import pytest
from src.infrastructure.encryption.aes_gcm_encryptor import AESGCMEncryptor
from src.shared.exceptions import EncryptionError, DecryptionError, InvalidPasswordError


class TestAESGCMEncryptor:
    """Test suite for AES-GCM encryption implementation."""

    @pytest.fixture
    def encryptor(self):
        """Create an encryptor instance."""
        return AESGCMEncryptor()

    @pytest.fixture
    def sample_data(self):
        """Sample plaintext data for testing."""
        return b"This is a test message for encryption."

    @pytest.fixture
    def sample_password(self):
        """Sample password for testing."""
        return "Test_Password_123!"

    def test_encrypt_decrypt_roundtrip(self, encryptor, sample_data, sample_password):
        """Test that data can be encrypted and then decrypted back to original."""
        # Encrypt
        encrypted = encryptor.encrypt(sample_data, sample_password)
        
        # Verify encrypted data is different from plaintext
        assert encrypted != sample_data
        assert len(encrypted) > len(sample_data)
        
        # Decrypt
        decrypted = encryptor.decrypt(encrypted, sample_password)
        
        # Verify decrypted matches original
        assert decrypted == sample_data

    def test_encrypt_produces_different_output_each_time(
        self, encryptor, sample_data, sample_password
    ):
        """Test that encrypting the same data twice produces different ciphertext (due to random salt/nonce)."""
        encrypted1 = encryptor.encrypt(sample_data, sample_password)
        encrypted2 = encryptor.encrypt(sample_data, sample_password)
        
        # Different ciphertext due to random salt and nonce
        assert encrypted1 != encrypted2
        
        # But both should decrypt to the same plaintext
        assert encryptor.decrypt(encrypted1, sample_password) == sample_data
        assert encryptor.decrypt(encrypted2, sample_password) == sample_data

    def test_wrong_password_raises_invalid_password_error(
        self, encryptor, sample_data, sample_password
    ):
        """Test that decrypting with wrong password raises InvalidPasswordError."""
        encrypted = encryptor.encrypt(sample_data, sample_password)
        
        with pytest.raises(InvalidPasswordError) as exc_info:
            encryptor.decrypt(encrypted, "WrongPassword123!")
        
        assert "Authentication failed" in str(exc_info.value)

    def test_is_encrypted_detects_encrypted_data(self, encryptor, sample_data, sample_password):
        """Test that is_encrypted correctly identifies encrypted data."""
        encrypted = encryptor.encrypt(sample_data, sample_password)
        
        assert encryptor.is_encrypted(encrypted) is True

    def test_is_encrypted_rejects_plaintext(self, encryptor, sample_data):
        """Test that is_encrypted returns False for plaintext data."""
        assert encryptor.is_encrypted(sample_data) is False

    def test_is_encrypted_rejects_invalid_header(self, encryptor):
        """Test that is_encrypted returns False for data with wrong magic header."""
        fake_data = b"WRONGHEADER" + b"\x00" * 100
        
        assert encryptor.is_encrypted(fake_data) is False

    def test_is_encrypted_rejects_wrong_version(self, encryptor, sample_data, sample_password):
        """Test that is_encrypted returns False for data with unsupported version."""
        encrypted = encryptor.encrypt(sample_data, sample_password)
        
        # Modify version byte (position 6 after MAGIC_HEADER)
        corrupted = bytearray(encrypted)
        corrupted[6] = 99  # Invalid version number
        
        assert encryptor.is_encrypted(bytes(corrupted)) is False

    def test_decrypt_corrupted_data_raises_decryption_error(
        self, encryptor, sample_data, sample_password
    ):
        """Test that decrypting corrupted data raises DecryptionError."""
        encrypted = encryptor.encrypt(sample_data, sample_password)
        
        # Corrupt the ciphertext (last part contains ciphertext + tag)
        corrupted = bytearray(encrypted)
        corrupted[-10] ^= 0xFF  # Flip bits in ciphertext
        
        with pytest.raises(DecryptionError):
            encryptor.decrypt(bytes(corrupted), sample_password)

    def test_decrypt_truncated_data_raises_decryption_error(self, encryptor):
        """Test that decrypting truncated data raises DecryptionError."""
        # Create data that's too short
        truncated = b"SAGENC\x01" + b"\x00" * 10
        
        with pytest.raises(DecryptionError) as exc_info:
            encryptor.decrypt(truncated, "password")
        
        assert "too short" in str(exc_info.value)

    def test_encrypt_empty_data(self, encryptor, sample_password):
        """Test that encrypting empty data works correctly."""
        empty_data = b""
        
        encrypted = encryptor.encrypt(empty_data, sample_password)
        decrypted = encryptor.decrypt(encrypted, sample_password)
        
        # Note: GCM can encrypt empty data - it will just contain the authentication tag
        assert decrypted == empty_data

    def test_encrypt_large_data(self, encryptor, sample_password):
        """Test that encrypting large data works correctly."""
        large_data = b"X" * 1_000_000  # 1 MB
        
        encrypted = encryptor.encrypt(large_data, sample_password)
        decrypted = encryptor.decrypt(encrypted, sample_password)
        
        assert decrypted == large_data

    def test_encrypt_unicode_data(self, encryptor, sample_password):
        """Test that encrypting UTF-8 encoded Unicode data works."""
        unicode_text = "Hello 世界 🌍 Ελληνικά Русский"
        unicode_data = unicode_text.encode('utf-8')
        
        encrypted = encryptor.encrypt(unicode_data, sample_password)
        decrypted = encryptor.decrypt(encrypted, sample_password)
        
        assert decrypted == unicode_data
        assert decrypted.decode('utf-8') == unicode_text

    def test_password_with_special_characters(self, encryptor, sample_data):
        """Test that passwords with special characters work correctly."""
        special_password = "P@ssw0rd!#$%^&*()_+-=[]{}|;:',.<>?/~`"
        
        encrypted = encryptor.encrypt(sample_data, special_password)
        decrypted = encryptor.decrypt(encrypted, special_password)
        
        assert decrypted == sample_data

    def test_very_long_password(self, encryptor, sample_data):
        """Test that very long passwords work correctly."""
        long_password = "a" * 1000
        
        encrypted = encryptor.encrypt(sample_data, long_password)
        decrypted = encryptor.decrypt(encrypted, long_password)
        
        assert decrypted == sample_data

    def test_empty_password_works(self, encryptor, sample_data):
        """Test that empty password works (though not recommended in practice)."""
        empty_password = ""
        
        encrypted = encryptor.encrypt(sample_data, empty_password)
        decrypted = encryptor.decrypt(encrypted, empty_password)
        
        assert decrypted == sample_data

    def test_decrypt_with_invalid_magic_header_raises_error(self, encryptor):
        """Test that decrypting data with invalid magic header raises DecryptionError."""
        invalid_data = b"INVALID" + b"\x00" * 100
        
        with pytest.raises(DecryptionError) as exc_info:
            encryptor.decrypt(invalid_data, "password")
        
        assert "Not an encrypted file" in str(exc_info.value)

    def test_encrypted_data_has_correct_structure(self, encryptor, sample_data, sample_password):
        """Test that encrypted data has the expected structure."""
        encrypted = encryptor.encrypt(sample_data, sample_password)
        
        # Check magic header (6 bytes)
        assert encrypted[:6] == b"SAGENC"
        
        # Check version (1 byte)
        assert encrypted[6] == 1
        
        # Check minimum length: MAGIC(6) + VERSION(1) + SALT(32) + NONCE(12) + TAG(16) = 67 bytes minimum
        assert len(encrypted) >= 67

    def test_salt_is_random(self, encryptor, sample_data, sample_password):
        """Test that each encryption uses a different random salt."""
        encrypted1 = encryptor.encrypt(sample_data, sample_password)
        encrypted2 = encryptor.encrypt(sample_data, sample_password)
        
        # Extract salt from position 7 to 39 (after magic header and version)
        salt1 = encrypted1[7:39]
        salt2 = encrypted2[7:39]
        
        # Salts should be different
        assert salt1 != salt2

    def test_nonce_is_random(self, encryptor, sample_data, sample_password):
        """Test that each encryption uses a different random nonce."""
        encrypted1 = encryptor.encrypt(sample_data, sample_password)
        encrypted2 = encryptor.encrypt(sample_data, sample_password)
        
        # Extract nonce from position 39 to 51 (after magic header, version, and salt)
        nonce1 = encrypted1[39:51]
        nonce2 = encrypted2[39:51]
        
        # Nonces should be different
        assert nonce1 != nonce2
