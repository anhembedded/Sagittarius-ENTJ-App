"""Recreate directory request DTO."""

from dataclasses import dataclass
from typing import Optional, Callable

from ...domain.models.snapshot import DirectorySnapshot


@dataclass
class RecreateRequest:
    """Request data for recreating a directory from snapshot."""
    
    snapshot: DirectorySnapshot
    output_path: str
    progress_callback: Optional[Callable[[int, int], None]] = None
    log_callback: Optional[Callable[[str], None]] = None
    
    def __post_init__(self):
        """Validate request data."""
        if not self.output_path:
            raise ValueError("output_path cannot be empty")
        if self.snapshot is None:
            raise ValueError("snapshot cannot be None")
