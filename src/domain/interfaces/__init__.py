"""Domain interfaces (abstractions)."""

from .repository import ISnapshotRepository
from .encoder import IContentEncoder
from .file_system import IFileSystemService

__all__ = ['ISnapshotRepository', 'IContentEncoder', 'IFileSystemService']
