"""Recreate directory use case."""

import os

from ...domain.models.snapshot import DirectorySnapshot
from ...domain.interfaces.file_system import IFileSystemService
from ...shared.utils import get_relative_path
from ...shared.exceptions import FileSystemError
from ..dto.recreate_request import RecreateRequest


class RecreateDirectoryUseCase:
    """Use case for recreating a directory structure from a snapshot."""
    
    def __init__(self, file_system: IFileSystemService):
        """
        Initialize the use case.
        
        Args:
            file_system: File system service for directory and file operations.
        """
        self._file_system = file_system
    
    def execute(self, request: RecreateRequest) -> None:
        """
        Execute the recreate directory use case.
        
        Args:
            request: Recreate request with parameters.
            
        Raises:
            FileSystemError: If directory recreation fails.
        """
        snapshot = request.snapshot
        output_path = request.output_path
        
        if request.log_callback:
            request.log_callback(f"🏗️ Starting recreation in: {output_path}")
        
        # Ensure output directory exists
        self._file_system.create_directory(output_path)
        
        # Create all subdirectories
        dir_count = 0
        for directory in snapshot.directories:
            dir_path = os.path.join(output_path, directory.relative_path.replace('/', os.sep))
            try:
                self._file_system.create_directory(dir_path)
                dir_count += 1
            except FileSystemError as e:
                if request.log_callback:
                    request.log_callback(f"  [Error creating dir {directory.relative_path}] -> {e}")
        
        # Recreate all files
        total_files = snapshot.get_file_count()
        processed = 0
        
        if request.progress_callback:
            request.progress_callback(0, total_files)
        
        for file_entry in snapshot.files:
            try:
                # Construct full file path
                file_path = os.path.join(
                    output_path,
                    file_entry.relative_path.replace('/', os.sep)
                )
                
                # Write file content
                self._file_system.write_file(file_path, file_entry.content)
                
                processed += 1
                
                if request.log_callback:
                    request.log_callback(f"  [Decode {processed}/{total_files}] -> {file_entry.relative_path}")
                
                if request.progress_callback:
                    request.progress_callback(processed, total_files)
                    
            except FileSystemError as e:
                if request.log_callback:
                    request.log_callback(f"  [Error writing {file_entry.relative_path}] -> {e}")
                # Continue processing other files
        
        if request.log_callback:
            log_msg = (f"✅ Recreation complete. Created {dir_count} dirs, "
                      f"processed {processed}/{total_files} files.")
            request.log_callback(log_msg)
