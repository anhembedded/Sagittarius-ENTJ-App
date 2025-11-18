"""Base64 content encoder implementation."""

import base64
from typing import Union

from ...domain.interfaces.encoder import IContentEncoder
from ...shared.exceptions import EncodingError


class Base64Encoder(IContentEncoder):
    """Encodes and decodes content using Base64 encoding."""
    
    def encode(self, content: bytes) -> str:
        """
        Encode binary content to Base64 string.
        
        Args:
            content: Binary content to encode.
            
        Returns:
            Base64 encoded string.
            
        Raises:
            EncodingError: If encoding fails.
        """
        try:
            encoded = base64.b64encode(content)
            return encoded.decode('utf-8')
        except Exception as e:
            raise EncodingError(f"Failed to encode content: {e}") from e
    
    def decode(self, encoded: str) -> bytes:
        """
        Decode Base64 string back to binary content.
        
        Args:
            encoded: Base64 encoded string.
            
        Returns:
            Decoded binary content.
            
        Raises:
            EncodingError: If decoding fails.
        """
        try:
            return base64.b64decode(encoded)
        except Exception as e:
            raise EncodingError(f"Failed to decode content: {e}") from e
