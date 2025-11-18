"""Content encoder interface."""

from abc import ABC, abstractmethod


class IContentEncoder(ABC):
    """Interface for encoding and decoding file content."""
    
    @abstractmethod
    def encode(self, content: bytes) -> str:
        """
        Encode binary content to string.
        
        Args:
            content: Binary content to encode.
            
        Returns:
            Encoded string representation.
            
        Raises:
            EncodingError: If encoding fails.
        """
        pass
    
    @abstractmethod
    def decode(self, encoded: str) -> bytes:
        """
        Decode string back to binary content.
        
        Args:
            encoded: Encoded string representation.
            
        Returns:
            Decoded binary content.
            
        Raises:
            EncodingError: If decoding fails.
        """
        pass
