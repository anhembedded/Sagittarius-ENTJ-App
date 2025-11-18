"""JSON snapshot repository implementation."""

import json
import os
from typing import Dict, Any

from ...domain.interfaces.repository import ISnapshotRepository
from ...domain.interfaces.encoder import IContentEncoder
from ...domain.models.snapshot import DirectorySnapshot
from ...domain.models.file_entry import FileEntry
from ...shared.exceptions import (
    RepositoryError, 
    SnapshotNotFoundError, 
    InvalidSnapshotError
)


class JsonSnapshotRepository(ISnapshotRepository):
    """Persists snapshots as JSON files."""
    
    def __init__(self, encoder: IContentEncoder):
        """
        Initialize the repository.
        
        Args:
            encoder: Content encoder for file content.
        """
        self._encoder = encoder
    
    def save(self, snapshot: DirectorySnapshot, path: str) -> None:
        """
        Save a snapshot to a JSON file.
        
        Args:
            snapshot: The snapshot to save.
            path: The file path where to save the snapshot.
            
        Raises:
            RepositoryError: If saving fails.
        """
        try:
            # Validate snapshot before saving
            snapshot.validate()
            
            # Encode all file contents
            for file_entry in snapshot.files:
                encoded = self._encoder.encode(file_entry.content)
                file_entry.set_encoded_content(encoded)
            
            # Convert to dict
            data = snapshot.to_dict()
            
            # Ensure parent directory exists
            parent_dir = os.path.dirname(path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            
            # Write JSON
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except (OSError, IOError) as e:
            raise RepositoryError(f"Failed to save snapshot to '{path}': {e}") from e
        except Exception as e:
            raise RepositoryError(f"Unexpected error saving snapshot: {e}") from e
    
    def load(self, path: str) -> DirectorySnapshot:
        """
        Load a snapshot from a JSON file.
        
        Args:
            path: The file path to load the snapshot from.
            
        Returns:
            The loaded DirectorySnapshot instance.
            
        Raises:
            SnapshotNotFoundError: If the snapshot file doesn't exist.
            InvalidSnapshotError: If the snapshot data is corrupted.
            RepositoryError: If loading fails for other reasons.
        """
        if not self.exists(path):
            raise SnapshotNotFoundError(f"Snapshot file not found: {path}")
        
        try:
            # Read JSON
            with open(path, 'r', encoding='utf-8') as f:
                data: Dict[str, Any] = json.load(f)
            
            # Validate required fields
            if 'files' not in data:
                raise InvalidSnapshotError("Snapshot is missing 'files' field")
            
            # Decode file contents
            files: list[FileEntry] = []
            for file_data in data['files']:
                if 'path' not in file_data or 'content_base64' not in file_data:
                    raise InvalidSnapshotError(
                        "File entry missing required fields (path, content_base64)"
                    )
                
                # Decode content
                content = self._encoder.decode(file_data['content_base64'])
                
                # Create FileEntry
                file_entry = FileEntry.from_dict(file_data, content)
                files.append(file_entry)
            
            # Create snapshot
            snapshot = DirectorySnapshot.from_dict(data, files)
            
            # Validate snapshot
            snapshot.validate()
            
            return snapshot
            
        except json.JSONDecodeError as e:
            raise InvalidSnapshotError(f"Invalid JSON in snapshot file: {e}") from e
        except (OSError, IOError) as e:
            raise RepositoryError(f"Failed to load snapshot from '{path}': {e}") from e
        except InvalidSnapshotError:
            raise
        except Exception as e:
            raise RepositoryError(f"Unexpected error loading snapshot: {e}") from e
    
    def exists(self, path: str) -> bool:
        """Check if a snapshot exists at the given path."""
        return os.path.isfile(path)
