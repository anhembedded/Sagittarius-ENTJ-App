"""File system service implementation."""

import os
from typing import List, Callable, Optional

from ...domain.interfaces.file_system import IFileSystemService
from ...shared.exceptions import FileSystemError
from ...shared.utils import get_file_extension


class FileSystemService(IFileSystemService):
    """Concrete implementation of file system operations."""
    
    def directory_exists(self, path: str) -> bool:
        """Check if a directory exists."""
        return os.path.isdir(path)
    
    def create_directory(self, path: str) -> None:
        """
        Create a directory (including parent directories).
        
        Args:
            path: The directory path to create.
            
        Raises:
            FileSystemError: If directory creation fails.
        """
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            raise FileSystemError(f"Failed to create directory '{path}': {e}") from e
    
    def list_files(
        self, 
        root_path: str, 
        extensions: List[str],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> List[str]:
        """
        List all files in a directory tree matching given extensions.
        
        Args:
            root_path: The root directory to scan.
            extensions: List of file extensions to include.
            progress_callback: Optional callback for progress updates.
            
        Returns:
            List of absolute file paths.
            
        Raises:
            FileSystemError: If directory traversal fails.
        """
        if not self.directory_exists(root_path):
            raise FileSystemError(f"Directory does not exist: {root_path}")
        
        # Normalize extensions to lowercase
        extensions_lower = [ext.lower() for ext in extensions]
        
        matching_files: List[str] = []
        
        try:
            # First pass: count total files for progress
            total_files = 0
            if progress_callback:
                for _, _, filenames in os.walk(root_path):
                    for filename in filenames:
                        ext = get_file_extension(filename)
                        if ext in extensions_lower:
                            total_files += 1
                progress_callback(0, total_files)
            
            # Second pass: collect matching files
            processed = 0
            for dirpath, _, filenames in os.walk(root_path):
                for filename in filenames:
                    ext = get_file_extension(filename)
                    if ext in extensions_lower:
                        file_path = os.path.join(dirpath, filename)
                        matching_files.append(file_path)
                        
                        processed += 1
                        if progress_callback:
                            progress_callback(processed, total_files)
            
        except OSError as e:
            raise FileSystemError(f"Failed to scan directory '{root_path}': {e}") from e
        
        return matching_files
    
    def read_file(self, path: str) -> bytes:
        """
        Read file content as binary.
        
        Args:
            path: The file path to read.
            
        Returns:
            File content as bytes.
            
        Raises:
            FileSystemError: If file reading fails.
        """
        try:
            with open(path, 'rb') as f:
                return f.read()
        except OSError as e:
            raise FileSystemError(f"Failed to read file '{path}': {e}") from e
    
    def write_file(self, path: str, content: bytes) -> None:
        """
        Write binary content to a file.
        
        Args:
            path: The file path to write to.
            content: Binary content to write.
            
        Raises:
            FileSystemError: If file writing fails.
        """
        try:
            # Ensure parent directory exists
            parent_dir = os.path.dirname(path)
            if parent_dir:
                self.create_directory(parent_dir)
            
            with open(path, 'wb') as f:
                f.write(content)
        except OSError as e:
            raise FileSystemError(f"Failed to write file '{path}': {e}") from e
    
    def get_file_size(self, path: str) -> int:
        """
        Get the size of a file in bytes.
        
        Args:
            path: The file path.
            
        Returns:
            File size in bytes.
            
        Raises:
            FileSystemError: If unable to get file size.
        """
        try:
            return os.path.getsize(path)
        except OSError as e:
            raise FileSystemError(f"Failed to get size of file '{path}': {e}") from e
