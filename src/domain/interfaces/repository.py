"""Snapshot repository interface."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.snapshot import DirectorySnapshot


class ISnapshotRepository(ABC):
    """Interface for persisting and loading directory snapshots."""
    
    @abstractmethod
    def save(self, snapshot: 'DirectorySnapshot', path: str) -> None:
        """
        Save a snapshot to persistent storage.
        
        Args:
            snapshot: The snapshot to save.
            path: The file path where to save the snapshot.
            
        Raises:
            RepositoryError: If saving fails.
        """
        pass
    
    @abstractmethod
    def load(self, path: str) -> 'DirectorySnapshot':
        """
        Load a snapshot from persistent storage.
        
        Args:
            path: The file path to load the snapshot from.
            
        Returns:
            The loaded DirectorySnapshot instance.
            
        Raises:
            SnapshotNotFoundError: If the snapshot file doesn't exist.
            InvalidSnapshotError: If the snapshot data is corrupted.
            RepositoryError: If loading fails for other reasons.
        """
        pass
    
    @abstractmethod
    def exists(self, path: str) -> bool:
        """
        Check if a snapshot exists at the given path.
        
        Args:
            path: The file path to check.
            
        Returns:
            True if snapshot exists, False otherwise.
        """
        pass
