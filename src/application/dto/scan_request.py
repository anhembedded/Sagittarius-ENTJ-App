"""Scan directory request DTO."""

from dataclasses import dataclass
from typing import List, Optional, Callable


@dataclass
class ScanRequest:
    """Request data for scanning a directory."""
    
    root_path: str
    extensions: List[str]
    progress_callback: Optional[Callable[[int, int], None]] = None
    log_callback: Optional[Callable[[str], None]] = None
    
    def __post_init__(self):
        """Validate request data."""
        if not self.root_path:
            raise ValueError("root_path cannot be empty")
        if not self.extensions:
            raise ValueError("extensions list cannot be empty")
