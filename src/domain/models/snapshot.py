"""Directory snapshot domain model."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional

from .file_entry import FileEntry
from .directory_entry import DirectoryEntry
from ...shared.exceptions import ValidationError


@dataclass
class DirectorySnapshot:
    """
    Represents a complete snapshot of a directory structure.
    
    This is the main domain aggregate root.
    """
    
    root_path: str
    directories: List[DirectoryEntry] = field(default_factory=list)
    files: List[FileEntry] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_directory(self, relative_path: str) -> None:
        """
        Add a directory to the snapshot.
        
        Args:
            relative_path: Relative path of the directory.
        """
        if relative_path and relative_path != '.':
            directory = DirectoryEntry(relative_path=relative_path)
            self.directories.append(directory)
    
    def add_file(self, file_entry: FileEntry) -> None:
        """
        Add a file to the snapshot.
        
        Args:
            file_entry: The FileEntry to add.
        """
        self.files.append(file_entry)
    
    def get_file_count(self) -> int:
        """Get the total number of files in the snapshot."""
        return len(self.files)
    
    def get_directory_count(self) -> int:
        """Get the total number of directories in the snapshot."""
        return len(self.directories)
    
    def get_total_size(self) -> int:
        """
        Get the total size of all files in bytes.
        
        Returns:
            Total size in bytes.
        """
        return sum(file.size for file in self.files)
    
    def validate(self) -> bool:
        """
        Validate the snapshot integrity.
        
        Returns:
            True if snapshot is valid.
            
        Raises:
            ValidationError: If snapshot is invalid.
        """
        if not self.root_path:
            raise ValidationError("Snapshot must have a root_path")
        
        # Validate all files have valid checksums
        for file_entry in self.files:
            if not file_entry.validate_checksum():
                raise ValidationError(
                    f"Invalid checksum for file: {file_entry.relative_path}"
                )
        
        # Check for duplicate paths
        file_paths = [f.relative_path for f in self.files]
        if len(file_paths) != len(set(file_paths)):
            raise ValidationError("Snapshot contains duplicate file paths")
        
        dir_paths = [d.relative_path for d in self.directories]
        if len(dir_paths) != len(set(dir_paths)):
            raise ValidationError("Snapshot contains duplicate directory paths")
        
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert snapshot to dictionary representation.
        
        Returns:
            Dictionary suitable for JSON serialization.
        """
        return {
            'root_path': self.root_path,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata,
            'directories': [d.relative_path for d in self.directories],
            'files': [f.to_dict() for f in self.files]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], files: List[FileEntry]) -> 'DirectorySnapshot':
        """
        Create snapshot from dictionary representation.
        
        Args:
            data: Dictionary containing snapshot metadata.
            files: List of FileEntry instances with decoded content.
            
        Returns:
            DirectorySnapshot instance.
        """
        created_at = datetime.fromisoformat(data['created_at']) if 'created_at' in data else datetime.now()
        
        snapshot = cls(
            root_path=data.get('root_path', ''),
            created_at=created_at,
            metadata=data.get('metadata', {})
        )
        
        # Add directories
        for dir_path in data.get('directories', []):
            snapshot.add_directory(dir_path)
        
        # Add files
        for file_entry in files:
            snapshot.add_file(file_entry)
        
        return snapshot
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get snapshot statistics.
        
        Returns:
            Dictionary containing snapshot statistics.
        """
        return {
            'root_path': self.root_path,
            'created_at': self.created_at.isoformat(),
            'directory_count': self.get_directory_count(),
            'file_count': self.get_file_count(),
            'total_size_bytes': self.get_total_size(),
            'file_extensions': self._get_extension_counts()
        }
    
    def _get_extension_counts(self) -> Dict[str, int]:
        """Get counts of files by extension."""
        extension_counts: Dict[str, int] = {}
        for file in self.files:
            ext = file.get_extension() or '(no extension)'
            extension_counts[ext] = extension_counts.get(ext, 0) + 1
        return extension_counts
    
    def __str__(self) -> str:
        return (f"Snapshot(root='{self.root_path}', "
                f"{self.get_directory_count()} dirs, "
                f"{self.get_file_count()} files)")
    
    def __repr__(self) -> str:
        return (f"DirectorySnapshot(root_path='{self.root_path}', "
                f"directories={len(self.directories)}, "
                f"files={len(self.files)})")
