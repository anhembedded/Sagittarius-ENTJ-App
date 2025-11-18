"""JSON snapshot repository implementation."""

import json
import os
from typing import Dict, Any, Optional

from ...domain.interfaces.repository import ISnapshotRepository
from ...domain.interfaces.encoder import IContentEncoder
from ...domain.interfaces.encryption import IEncryptionService
from ...domain.models.snapshot import DirectorySnapshot
from ...domain.models.file_entry import FileEntry
from ...shared.exceptions import (
    RepositoryError, 
    SnapshotNotFoundError, 
    InvalidSnapshotError,
    DecryptionError
)


class JsonSnapshotRepository(ISnapshotRepository):
    """Persists snapshots as JSON files with optional encryption."""
    
    def __init__(self, encoder: IContentEncoder, 
                 encryption_service: Optional[IEncryptionService] = None):
        """
        Initialize the repository.
        
        Args:
            encoder: Content encoder for file content.
            encryption_service: Optional encryption service for encrypted snapshots.
        """
        self._encoder = encoder
        self._encryption_service = encryption_service
    
    def save(self, snapshot: DirectorySnapshot, path: str, 
             password: Optional[str] = None) -> None:
        """
        Save a snapshot to a JSON file with optional encryption.
        
        Args:
            snapshot: The snapshot to save.
            path: The file path where to save the snapshot.
            password: Optional password for encryption.
            
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
            
            # Convert to JSON string
            json_str = json.dumps(data, indent=2, ensure_ascii=False)
            json_bytes = json_str.encode('utf-8')
            
            # Encrypt if password provided
            if password and self._encryption_service:
                json_bytes = self._encryption_service.encrypt(json_bytes, password)
            
            # Ensure parent directory exists
            parent_dir = os.path.dirname(path)
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
            
            # Write to file (binary mode for encryption support)
            with open(path, 'wb') as f:
                f.write(json_bytes)
                
        except (OSError, IOError) as e:
            raise RepositoryError(f"Failed to save snapshot to '{path}': {e}") from e
        except Exception as e:
            raise RepositoryError(f"Unexpected error saving snapshot: {e}") from e
    
    def load(self, path: str, password: Optional[str] = None) -> DirectorySnapshot:
        """
        Load a snapshot from a JSON file with automatic encryption detection.
        
        Args:
            path: The file path to load the snapshot from.
            password: Optional password for decryption (required if file is encrypted).
            
        Returns:
            The loaded DirectorySnapshot instance.
            
        Raises:
            SnapshotNotFoundError: If the snapshot file doesn't exist.
            InvalidSnapshotError: If the snapshot data is corrupted.
            DecryptionError: If file is encrypted and password is not provided.
            RepositoryError: If loading fails for other reasons.
        """
        if not self.exists(path):
            raise SnapshotNotFoundError(f"Snapshot file not found: {path}")
        
        try:
            # Read file as bytes
            with open(path, 'rb') as f:
                data_bytes = f.read()
            
            # Check if encrypted and decrypt if needed
            if self._encryption_service and self._encryption_service.is_encrypted(data_bytes):
                if not password:
                    raise DecryptionError(
                        "This snapshot is encrypted. Please provide a password to decrypt it."
                    )
                # Decrypt
                data_bytes = self._encryption_service.decrypt(data_bytes, password)
            
            # Parse JSON
            json_str = data_bytes.decode('utf-8')
            data: Dict[str, Any] = json.loads(json_str)
            
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
            
        except DecryptionError:
            raise
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
