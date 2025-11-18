"""Save snapshot use case."""

from ...domain.models.snapshot import DirectorySnapshot
from ...domain.interfaces.repository import ISnapshotRepository
from ...shared.exceptions import RepositoryError


class SaveSnapshotUseCase:
    """Use case for saving a snapshot to persistent storage."""
    
    def __init__(self, repository: ISnapshotRepository):
        """
        Initialize the use case.
        
        Args:
            repository: Snapshot repository for persistence.
        """
        self._repository = repository
    
    def execute(self, snapshot: DirectorySnapshot, path: str) -> None:
        """
        Execute the save snapshot use case.
        
        Args:
            snapshot: The snapshot to save.
            path: File path where to save the snapshot.
            
        Raises:
            RepositoryError: If saving fails.
        """
        # Validate snapshot before saving
        snapshot.validate()
        
        # Save using repository
        self._repository.save(snapshot, path)
