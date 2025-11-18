"""File entry domain model."""

from dataclasses import dataclass, field
from typing import Optional
import hashlib

from ...shared.utils import normalize_path, get_file_extension
from ...shared.exceptions import ValidationError


@dataclass
class FileEntry:
    """Represents a file in the snapshot."""
    
    relative_path: str
    content: bytes
    size: int = field(init=False)
    checksum: str = field(init=False)
    _encoded_content: Optional[str] = field(default=None, init=False, repr=False)
    
    def __post_init__(self):
        """Calculate derived fields after initialization."""
        self.relative_path = normalize_path(self.relative_path)
        self.size = len(self.content)
        self.checksum = self._calculate_checksum(self.content)
    
    @staticmethod
    def _calculate_checksum(content: bytes) -> str:
        """Calculate SHA-256 checksum of content."""
        return hashlib.sha256(content).hexdigest()
    
    def validate_checksum(self) -> bool:
        """
        Validate that current content matches the stored checksum.
        
        Returns:
            True if checksum is valid, False otherwise.
        """
        current_checksum = self._calculate_checksum(self.content)
        return current_checksum == self.checksum
    
    def get_extension(self) -> str:
        """
        Get the file extension.
        
        Returns:
            File extension (e.g., '.py', '.txt') or empty string.
        """
        return get_file_extension(self.relative_path)
    
    def set_encoded_content(self, encoded: str) -> None:
        """Set the encoded content (used during serialization)."""
        self._encoded_content = encoded
    
    def get_encoded_content(self) -> Optional[str]:
        """Get the encoded content if available."""
        return self._encoded_content
    
    def to_dict(self, include_content: bool = True) -> dict:
        """
        Convert to dictionary representation.
        
        Args:
            include_content: Whether to include encoded content in the dict.
            
        Returns:
            Dictionary representation.
            
        Raises:
            ValidationError: If include_content is True but no encoded content is set.
        """
        data = {
            'path': self.relative_path,
            'size': self.size,
            'checksum': self.checksum
        }
        
        if include_content:
            if self._encoded_content is None:
                raise ValidationError(
                    f"File '{self.relative_path}' has no encoded content. "
                    "Call set_encoded_content() first."
                )
            data['content_base64'] = self._encoded_content
        
        return data
    
    @classmethod
    def from_dict(cls, data: dict, content: bytes) -> 'FileEntry':
        """
        Create from dictionary representation.
        
        Args:
            data: Dictionary containing file metadata.
            content: Decoded binary content.
            
        Returns:
            FileEntry instance.
        """
        entry = cls(
            relative_path=data['path'],
            content=content
        )
        
        # Validate checksum if provided
        if 'checksum' in data:
            if entry.checksum != data['checksum']:
                raise ValidationError(
                    f"Checksum mismatch for file '{entry.relative_path}'. "
                    f"Expected {data['checksum']}, got {entry.checksum}"
                )
        
        return entry
    
    def __str__(self) -> str:
        return f"File({self.relative_path}, {self.size} bytes)"
    
    def __repr__(self) -> str:
        return (f"FileEntry(relative_path='{self.relative_path}', "
                f"size={self.size}, checksum='{self.checksum[:8]}...')")
