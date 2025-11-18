"""Encryption service interface."""

from abc import ABC, abstractmethod


class IEncryptionService(ABC):
    """Interface for encryption and decryption services."""
    
    @abstractmethod
    def encrypt(self, data: bytes, password: str) -> bytes:
        """
        Encrypt data using the provided password.
        
        Args:
            data: Raw data to encrypt.
            password: Password for encryption.
            
        Returns:
            Encrypted data with all necessary metadata (salt, nonce, etc.).
            
        Raises:
            EncryptionError: If encryption fails.
        """
        pass
    
    @abstractmethod
    def decrypt(self, encrypted_data: bytes, password: str) -> bytes:
        """
        Decrypt data using the provided password.
        
        Args:
            encrypted_data: Encrypted data with metadata.
            password: Password for decryption.
            
        Returns:
            Decrypted raw data.
            
        Raises:
            DecryptionError: If decryption fails.
            InvalidPasswordError: If password is incorrect.
        """
        pass
    
    @abstractmethod
    def is_encrypted(self, data: bytes) -> bool:
        """
        Check if data is encrypted.
        
        Args:
            data: Data to check.
            
        Returns:
            True if data is encrypted, False otherwise.
        """
        pass
