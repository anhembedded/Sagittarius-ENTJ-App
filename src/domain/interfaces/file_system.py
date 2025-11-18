"""File system service interface."""

from abc import ABC, abstractmethod
from typing import List, Callable, Optional


class IFileSystemService(ABC):
    """Interface for file system operations."""
    
    @abstractmethod
    def directory_exists(self, path: str) -> bool:
        """
        Check if a directory exists.
        
        Args:
            path: The directory path to check.
            
        Returns:
            True if directory exists, False otherwise.
        """
        pass
    
    @abstractmethod
    def create_directory(self, path: str) -> None:
        """
        Create a directory (including parent directories).
        
        Args:
            path: The directory path to create.
            
        Raises:
            FileSystemError: If directory creation fails.
        """
        pass
    
    @abstractmethod
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
            extensions: List of file extensions to include (e.g., ['.py', '.txt']).
            progress_callback: Optional callback for progress updates (current, total).
            
        Returns:
            List of absolute file paths.
            
        Raises:
            FileSystemError: If directory traversal fails.
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    def write_file(self, path: str, content: bytes) -> None:
        """
        Write binary content to a file.
        
        Args:
            path: The file path to write to.
            content: Binary content to write.
            
        Raises:
            FileSystemError: If file writing fails.
        """
        pass
    
    @abstractmethod
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
        pass
