"""Extension filter service."""

from typing import List, Set

from ...shared.utils import get_file_extension
from ...shared.constants import DEFAULT_EXTENSIONS


class ExtensionFilter:
    """Manages file extension filtering logic."""
    
    def __init__(self, extensions: List[str] = None):
        """
        Initialize the extension filter.
        
        Args:
            extensions: List of allowed extensions (e.g., ['.py', '.txt']).
                       If None, uses DEFAULT_EXTENSIONS.
        """
        if extensions is None:
            extensions = DEFAULT_EXTENSIONS.copy()
        
        # Normalize extensions to lowercase and ensure they start with '.'
        self._extensions: Set[str] = set()
        for ext in extensions:
            self.add_extension(ext)
    
    def add_extension(self, extension: str) -> None:
        """
        Add an extension to the filter.
        
        Args:
            extension: File extension (with or without leading dot).
        """
        # Ensure extension starts with '.' and is lowercase
        if not extension.startswith('.'):
            extension = '.' + extension
        self._extensions.add(extension.lower())
    
    def remove_extension(self, extension: str) -> None:
        """
        Remove an extension from the filter.
        
        Args:
            extension: File extension to remove.
        """
        if not extension.startswith('.'):
            extension = '.' + extension
        self._extensions.discard(extension.lower())
    
    def is_allowed(self, filename: str) -> bool:
        """
        Check if a filename matches the allowed extensions.
        
        Args:
            filename: The filename to check.
            
        Returns:
            True if the file extension is allowed, False otherwise.
        """
        ext = get_file_extension(filename)
        if not ext:
            return False
        return ext in self._extensions
    
    def get_extensions(self) -> List[str]:
        """
        Get the list of allowed extensions.
        
        Returns:
            Sorted list of extensions.
        """
        return sorted(self._extensions)
    
    def set_extensions(self, extensions: List[str]) -> None:
        """
        Replace all extensions with a new list.
        
        Args:
            extensions: New list of extensions.
        """
        self._extensions.clear()
        for ext in extensions:
            self.add_extension(ext)
    
    def clear(self) -> None:
        """Remove all extensions from the filter."""
        self._extensions.clear()
    
    def __len__(self) -> int:
        """Get the number of extensions in the filter."""
        return len(self._extensions)
    
    def __contains__(self, extension: str) -> bool:
        """Check if an extension is in the filter."""
        if not extension.startswith('.'):
            extension = '.' + extension
        return extension.lower() in self._extensions
    
    def __str__(self) -> str:
        return f"ExtensionFilter({', '.join(self.get_extensions())})"
    
    def __repr__(self) -> str:
        return f"ExtensionFilter(extensions={self.get_extensions()})"
