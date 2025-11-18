"""Scan directory use case."""

import os
from typing import Optional, Callable

from ...domain.models.snapshot import DirectorySnapshot
from ...domain.models.file_entry import FileEntry
from ...domain.services.extension_filter import ExtensionFilter
from ...domain.interfaces.file_system import IFileSystemService
from ...domain.interfaces.encoder import IContentEncoder
from ...shared.utils import get_relative_path
from ...shared.exceptions import FileSystemError
from ..dto.scan_request import ScanRequest


class ScanDirectoryUseCase:
    """Use case for scanning a directory and creating a snapshot."""
    
    def __init__(
        self,
        file_system: IFileSystemService,
        encoder: IContentEncoder
    ):
        """
        Initialize the use case.
        
        Args:
            file_system: File system service for directory operations.
            encoder: Content encoder for file content.
        """
        self._file_system = file_system
        self._encoder = encoder
    
    def execute(self, request: ScanRequest) -> DirectorySnapshot:
        """
        Execute the scan directory use case.
        
        Args:
            request: Scan request with parameters.
            
        Returns:
            DirectorySnapshot containing scanned files and directories.
            
        Raises:
            FileSystemError: If directory scanning fails.
        """
        # Validate directory exists
        if not self._file_system.directory_exists(request.root_path):
            raise FileSystemError(f"Directory does not exist: {request.root_path}")
        
        if request.log_callback:
            request.log_callback(f"🔍 Starting scan in: {request.root_path}")
        
        # Create snapshot
        snapshot = DirectorySnapshot(root_path=request.root_path)
        
        # List all matching files
        file_paths = self._file_system.list_files(
            request.root_path,
            request.extensions,
            request.progress_callback
        )
        
        if request.log_callback:
            request.log_callback(f"🔢 Found {len(file_paths)} files matching extensions.")
        
        # Collect directories from file paths
        directories_set = set()
        for file_path in file_paths:
            rel_path = get_relative_path(file_path, request.root_path)
            dir_path = os.path.dirname(rel_path)
            
            # Add all parent directories
            while dir_path and dir_path != '.':
                directories_set.add(dir_path)
                dir_path = os.path.dirname(dir_path)
        
        # Add directories to snapshot
        for dir_path in sorted(directories_set):
            snapshot.add_directory(dir_path)
        
        # Process files
        total_files = len(file_paths)
        for idx, file_path in enumerate(file_paths, 1):
            try:
                # Read file content
                content = self._file_system.read_file(file_path)
                
                # Create file entry
                rel_path = get_relative_path(file_path, request.root_path)
                file_entry = FileEntry(relative_path=rel_path, content=content)
                
                # Encode content for storage
                encoded = self._encoder.encode(content)
                file_entry.set_encoded_content(encoded)
                
                # Add to snapshot
                snapshot.add_file(file_entry)
                
                if request.log_callback:
                    request.log_callback(f"  [Encode {idx}/{total_files}] -> {rel_path}")
                
                if request.progress_callback:
                    request.progress_callback(idx, total_files)
                    
            except Exception as e:
                if request.log_callback:
                    request.log_callback(f"  [Error reading {file_path}] -> {e}")
                # Continue processing other files
        
        if request.log_callback:
            request.log_callback(
                f"📊 Scan complete. Found {snapshot.get_directory_count()} subdirs "
                f"and encoded {snapshot.get_file_count()} files."
            )
        
        return snapshot
