"""Utility helper functions."""

import os
from pathlib import Path
from typing import Optional


def normalize_path(path: str) -> str:
    """
    Normalize a file path for cross-platform compatibility.
    
    Args:
        path: The path to normalize.
        
    Returns:
        Normalized path with forward slashes.
    """
    return path.replace(os.sep, '/')


def ensure_directory(path: str) -> None:
    """
    Ensure a directory exists, creating it if necessary.
    
    Args:
        path: The directory path to create.
        
    Raises:
        OSError: If directory creation fails.
    """
    os.makedirs(path, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """
    Get the file extension from a filename.
    
    Args:
        filename: The filename to extract extension from.
        
    Returns:
        The file extension (including the dot) in lowercase, or empty string.
    """
    _, ext = os.path.splitext(filename)
    return ext.lower() if ext else ''


def get_relative_path(file_path: str, root_path: str) -> str:
    """
    Get the relative path of a file from a root directory.
    
    Args:
        file_path: The full file path.
        root_path: The root directory path.
        
    Returns:
        The relative path with forward slashes.
    """
    rel_path = os.path.relpath(file_path, root_path)
    return normalize_path(rel_path)


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes.
        
    Returns:
        Formatted string (e.g., "1.5 MB").
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def is_path_safe(path: str, base_path: Optional[str] = None) -> bool:
    """
    Check if a path is safe (no path traversal attempts).
    
    Args:
        path: The path to check.
        base_path: Optional base path to ensure path stays within.
        
    Returns:
        True if path is safe, False otherwise.
    """
    # Check for path traversal attempts
    if '..' in Path(path).parts:
        return False
    
    # If base path provided, ensure path stays within it
    if base_path:
        try:
            abs_path = os.path.abspath(os.path.join(base_path, path))
            abs_base = os.path.abspath(base_path)
            return abs_path.startswith(abs_base)
        except (ValueError, OSError):
            return False
    
    return True
