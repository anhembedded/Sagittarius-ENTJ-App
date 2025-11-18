"""Directory entry domain model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ...shared.utils import normalize_path


@dataclass
class DirectoryEntry:
    """Represents a directory in the snapshot."""
    
    relative_path: str
    created_at: Optional[datetime] = None
    
    def __post_init__(self):
        """Normalize path after initialization."""
        self.relative_path = normalize_path(self.relative_path)
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def get_depth(self) -> int:
        """
        Get the depth level of this directory.
        
        Returns:
            Depth level (0 for root-level directories).
        """
        if not self.relative_path or self.relative_path == '.':
            return 0
        return len(self.relative_path.split('/'))
    
    def to_dict(self) -> dict:
        """Convert to dictionary representation."""
        return {
            'relative_path': self.relative_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DirectoryEntry':
        """Create from dictionary representation."""
        created_at = None
        if data.get('created_at'):
            created_at = datetime.fromisoformat(data['created_at'])
        
        return cls(
            relative_path=data['relative_path'],
            created_at=created_at
        )
    
    def __str__(self) -> str:
        return f"Dir({self.relative_path})"
    
    def __repr__(self) -> str:
        return f"DirectoryEntry(relative_path='{self.relative_path}')"
