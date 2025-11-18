"""Copy operation view model."""

from typing import List, Optional
from PySide6.QtCore import QObject, Signal, QThreadPool

from ...di_container import DIContainer
from ...application.dto.scan_request import ScanRequest
from ...domain.models.snapshot import DirectorySnapshot
from ...shared.constants import SETTINGS_COPY_SOURCE_DIR, SETTINGS_COPY_JSON_PATH
from ..workers.async_worker import AsyncWorker


class CopyViewModel(QObject):
    """Manages state and logic for the Copy operation."""
    
    # Signals
    message_logged = Signal(str)
    status_update = Signal(str, int)
    progress_changed = Signal(int)
    progress_max_changed = Signal(int)
    operation_active = Signal(bool)
    scan_completed = Signal(object)  # DirectorySnapshot
    
    def __init__(self, container: DIContainer):
        """
        Initialize the Copy view model.
        
        Args:
            container: Dependency injection container.
        """
        super().__init__()
        self._container = container
        self._threadpool = QThreadPool()
        self._settings = container.get_settings_repository()
        self._current_snapshot: Optional[DirectorySnapshot] = None
        
        # Load saved paths
        self._source_dir = self._settings.get_string(SETTINGS_COPY_SOURCE_DIR, "")
        self._json_path = self._settings.get_string(SETTINGS_COPY_JSON_PATH, "")
    
    # Properties
    @property
    def source_dir(self) -> str:
        """Get the source directory path."""
        return self._source_dir
    
    @source_dir.setter
    def source_dir(self, value: str):
        """Set and persist the source directory path."""
        self._source_dir = value
        self._settings.set(SETTINGS_COPY_SOURCE_DIR, value)
    
    @property
    def json_path(self) -> str:
        """Get the JSON output path."""
        return self._json_path
    
    @json_path.setter
    def json_path(self, value: str):
        """Set and persist the JSON output path."""
        self._json_path = value
        self._settings.set(SETTINGS_COPY_JSON_PATH, value)
    
    @property
    def current_snapshot(self) -> Optional[DirectorySnapshot]:
        """Get the current snapshot if available."""
        return self._current_snapshot
    
    def scan_directory(self, root_path: str, extensions: List[str]) -> None:
        """
        Start scanning a directory asynchronously.
        
        Args:
            root_path: The directory to scan.
            extensions: List of file extensions to include.
        """
        self.operation_active.emit(True)
        self.message_logged.emit(f"🔍 Starting scan of: {root_path}")
        
        # Create request
        request = ScanRequest(
            root_path=root_path,
            extensions=extensions,
            progress_callback=self._on_scan_progress,
            log_callback=self._on_scan_log
        )
        
        # Create and configure worker
        use_case = self._container.get_scan_directory_use_case()
        worker = AsyncWorker(use_case.execute, request)
        
        # Connect signals
        worker.signals.result.connect(self._on_scan_completed)
        worker.signals.error.connect(self._on_scan_error)
        worker.signals.finished.connect(self._on_operation_finished)
        
        # Start worker
        self._threadpool.start(worker)
    
    def save_snapshot(self, snapshot: DirectorySnapshot, path: str) -> None:
        """
        Save a snapshot to JSON file asynchronously.
        
        Args:
            snapshot: The snapshot to save.
            path: The file path to save to.
        """
        self.operation_active.emit(True)
        self.message_logged.emit(f"💾 Saving snapshot to: {path}")
        
        # Create and configure worker
        use_case = self._container.get_save_snapshot_use_case()
        worker = AsyncWorker(use_case.execute, snapshot, path)
        
        # Connect signals
        worker.signals.result.connect(lambda: self._on_save_completed(path))
        worker.signals.error.connect(self._on_save_error)
        worker.signals.finished.connect(self._on_operation_finished)
        
        # Start worker
        self._threadpool.start(worker)
    
    def _on_scan_progress(self, current: int, total: int) -> None:
        """Handle scan progress updates."""
        if total > 0:
            self.progress_max_changed.emit(total)
            self.progress_changed.emit(current)
    
    def _on_scan_log(self, message: str) -> None:
        """Handle scan log messages."""
        self.message_logged.emit(message)
    
    def _on_scan_completed(self, snapshot: DirectorySnapshot) -> None:
        """Handle successful scan completion."""
        self._current_snapshot = snapshot
        self.message_logged.emit(
            f"✅ Scan completed: {snapshot.get_file_count()} files, "
            f"{snapshot.get_directory_count()} directories"
        )
        self.status_update.emit("Scan completed successfully", 5000)
        self.scan_completed.emit(snapshot)
    
    def _on_scan_error(self, error_msg: str) -> None:
        """Handle scan errors."""
        self.message_logged.emit(f"❌ Scan error: {error_msg}")
        self.status_update.emit("Scan failed", 5000)
    
    def _on_save_completed(self, path: str) -> None:
        """Handle successful save completion."""
        self.message_logged.emit(f"✅ Snapshot saved to: {path}")
        self.status_update.emit("Save completed successfully", 5000)
    
    def _on_save_error(self, error_msg: str) -> None:
        """Handle save errors."""
        self.message_logged.emit(f"❌ Save error: {error_msg}")
        self.status_update.emit("Save failed", 5000)
    
    def _on_operation_finished(self) -> None:
        """Handle operation completion (success or failure)."""
        self.operation_active.emit(False)
