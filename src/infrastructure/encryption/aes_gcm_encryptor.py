"""AES-256-GCM encryption implementation."""

import secrets
from typing import Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.backends import default_backend

from ...domain.interfaces.encryption import IEncryptionService
from ...shared.exceptions import EncryptionError, DecryptionError, InvalidPasswordError


class AESGCMEncryptor(IEncryptionService):
    """
    AES-256-GCM encryption with PBKDF2 key derivation.
    
    File format:
    [MAGIC_HEADER][VERSION][SALT][NONCE][CIPHERTEXT+TAG]
    
    - MAGIC_HEADER: 6 bytes - "SAGENC" to identify encrypted files
    - VERSION: 1 byte - encryption version for future compatibility
    - SALT: 32 bytes - random salt for PBKDF2 key derivation
    - NONCE: 12 bytes - random nonce for AES-GCM (96 bits)
    - CIPHERTEXT+TAG: variable - encrypted data + 16-byte auth tag
    """
    
    # File format constants
    MAGIC_HEADER = b"SAGENC"
    VERSION = 1
    SALT_SIZE = 32  # 256 bits
    NONCE_SIZE = 12  # 96 bits (recommended for GCM)
    KEY_SIZE = 32  # 256 bits for AES-256
    PBKDF2_ITERATIONS = 100000  # OWASP recommendation (2023)
    
    def encrypt(self, data: bytes, password: str) -> bytes:
        """
        Encrypt data using AES-256-GCM with password-based key.
        
        Args:
            data: Raw data to encrypt.
            password: Password for encryption.
        
        Returns:
            Encrypted data with metadata in custom format.
        
        Raises:
            EncryptionError: If encryption fails.
        """
        try:
            # Note: Empty password and data are technically allowed,
            # though not recommended for security
            pass            # Generate random salt and nonce
            salt = self._generate_salt()
            nonce = self._generate_nonce()
            
            # Derive encryption key from password using PBKDF2
            key = self._derive_key(password, salt)
            
            # Encrypt with AES-GCM (includes authentication tag)
            aesgcm = AESGCM(key)
            ciphertext = aesgcm.encrypt(nonce, data, None)
            
            # Build encrypted file format
            encrypted_data = (
                self.MAGIC_HEADER +
                bytes([self.VERSION]) +
                salt +
                nonce +
                ciphertext
            )
            
            return encrypted_data
            
        except EncryptionError:
            raise
        except Exception as e:
            raise EncryptionError(f"Encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_data: bytes, password: str) -> bytes:
        """
        Decrypt data using AES-256-GCM with password-based key.
        
        Args:
            encrypted_data: Encrypted data in custom format.
            password: Password for decryption.
            
        Returns:
            Decrypted raw data.
            
        Raises:
            DecryptionError: If file format is invalid.
            InvalidPasswordError: If password is incorrect or data is corrupted.
        """
        try:
            # Note: Empty password is technically allowed
            
            # Verify minimum size
            min_size = (
                len(self.MAGIC_HEADER) + 1 + 
                self.SALT_SIZE + self.NONCE_SIZE + 16
            )
            if len(encrypted_data) < min_size:
                raise DecryptionError("Invalid encrypted data: too short")
            
            # Verify magic header
            if not self.is_encrypted(encrypted_data):
                raise DecryptionError("Not an encrypted file (missing magic header)")
            
            # Parse file format
            offset = len(self.MAGIC_HEADER)
            
            # Extract version
            version = encrypted_data[offset]
            offset += 1
            
            if version != self.VERSION:
                raise DecryptionError(
                    f"Unsupported encryption version: {version} "
                    f"(expected {self.VERSION})"
                )
            
            # Extract salt
            salt = encrypted_data[offset:offset + self.SALT_SIZE]
            offset += self.SALT_SIZE
            
            if len(salt) != self.SALT_SIZE:
                raise DecryptionError("Invalid encrypted data: incomplete salt")
            
            # Extract nonce
            nonce = encrypted_data[offset:offset + self.NONCE_SIZE]
            offset += self.NONCE_SIZE
            
            if len(nonce) != self.NONCE_SIZE:
                raise DecryptionError("Invalid encrypted data: incomplete nonce")
            
            # Extract ciphertext (includes authentication tag)
            ciphertext = encrypted_data[offset:]
            
            if len(ciphertext) < 16:  # Minimum: empty data + 16-byte tag
                raise DecryptionError("Invalid encrypted data: incomplete ciphertext")
            
            # Derive key from password
            key = self._derive_key(password, salt)
            
            # Decrypt with AES-GCM (automatically verifies authentication tag)
            aesgcm = AESGCM(key)
            plaintext = aesgcm.decrypt(nonce, ciphertext, None)
            
            return plaintext
            
        except InvalidTag:
            # GCM authentication failed - wrong password or corrupted data
            raise InvalidPasswordError(
                "Authentication failed: wrong password or corrupted data"
            )
        except InvalidPasswordError:
            raise
        except DecryptionError:
            raise
        except Exception as e:
            raise DecryptionError(f"Decryption failed: {str(e)}")
    
    def is_encrypted(self, data: bytes) -> bool:
        """
        Check if data is encrypted by verifying magic header and version.
        
        Args:
            data: Data to check.
            
        Returns:
            True if data starts with encryption magic header and has correct version.
        """
        if not data or len(data) < len(self.MAGIC_HEADER) + 1:  # +1 for version
            return False
        
        if not data.startswith(self.MAGIC_HEADER):
            return False
        
        # Check version
        version = data[len(self.MAGIC_HEADER)]
        return version == self.VERSION
    
    def _derive_key(self, password: str, salt: bytes) -> bytes:
        """
        Derive encryption key from password using PBKDF2-HMAC-SHA256.
        
        Args:
            password: User password.
            salt: Random salt.
            
        Returns:
            Derived encryption key.
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt,
            iterations=self.PBKDF2_ITERATIONS,
            backend=default_backend()
        )
        return kdf.derive(password.encode('utf-8'))
    
    def _generate_salt(self) -> bytes:
        """Generate cryptographically secure random salt."""
        return secrets.token_bytes(self.SALT_SIZE)
    
    def _generate_nonce(self) -> bytes:
        """Generate cryptographically secure random nonce."""
        return secrets.token_bytes(self.NONCE_SIZE)
