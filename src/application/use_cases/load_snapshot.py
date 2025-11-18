"""Load snapshot use case."""

from ...domain.models.snapshot import DirectorySnapshot
from ...domain.interfaces.repository import ISnapshotRepository
from ...shared.exceptions import SnapshotNotFoundError, InvalidSnapshotError


class LoadSnapshotUseCase:
    """Use case for loading a snapshot from persistent storage."""
    
    def __init__(self, repository: ISnapshotRepository):
        """
        Initialize the use case.
        
        Args:
            repository: Snapshot repository for persistence.
        """
        self._repository = repository
    
    def execute(self, path: str) -> DirectorySnapshot:
        """
        Execute the load snapshot use case.
        
        Args:
            path: File path to load the snapshot from.
            
        Returns:
            Loaded DirectorySnapshot.
            
        Raises:
            SnapshotNotFoundError: If snapshot file doesn't exist.
            InvalidSnapshotError: If snapshot data is corrupted.
        """
        # Load using repository
        snapshot = self._repository.load(path)
        
        # Validate loaded snapshot
        snapshot.validate()
        
        return snapshot
