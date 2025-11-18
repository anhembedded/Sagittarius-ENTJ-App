"""Paste operation view model."""

from typing import Optional
from PySide6.QtCore import QObject, Signal, QThreadPool

from ...di_container import DIContainer
from ...application.dto.recreate_request import RecreateRequest
from ...domain.models.snapshot import DirectorySnapshot
from ...shared.constants import SETTINGS_PASTE_JSON_PATH, SETTINGS_PASTE_OUTPUT_DIR
from ..workers.async_worker import AsyncWorker


class PasteViewModel(QObject):
    """Manages state and logic for the Paste operation."""
    
    # Signals
    message_logged = Signal(str)
    status_update = Signal(str, int)
    progress_changed = Signal(int)
    progress_max_changed = Signal(int)
    operation_active = Signal(bool)
    load_completed = Signal(object)  # DirectorySnapshot
    
    def __init__(self, container: DIContainer):
        """
        Initialize the Paste view model.
        
        Args:
            container: Dependency injection container.
        """
        super().__init__()
        self._container = container
        self._threadpool = QThreadPool()
        self._settings = container.get_settings_repository()
        self._current_snapshot: Optional[DirectorySnapshot] = None
        
        # Load saved paths
        self._json_path = self._settings.get_string(SETTINGS_PASTE_JSON_PATH, "")
        self._output_dir = self._settings.get_string(SETTINGS_PASTE_OUTPUT_DIR, "")
    
    # Properties
    @property
    def json_path(self) -> str:
        """Get the JSON file path."""
        return self._json_path
    
    @json_path.setter
    def json_path(self, value: str):
        """Set and persist the JSON file path."""
        self._json_path = value
        self._settings.set(SETTINGS_PASTE_JSON_PATH, value)
    
    @property
    def output_dir(self) -> str:
        """Get the output directory path."""
        return self._output_dir
    
    @output_dir.setter
    def output_dir(self, value: str):
        """Set and persist the output directory path."""
        self._output_dir = value
        self._settings.set(SETTINGS_PASTE_OUTPUT_DIR, value)
    
    @property
    def current_snapshot(self) -> Optional[DirectorySnapshot]:
        """Get the current snapshot if available."""
        return self._current_snapshot
    
    def load_snapshot(self, path: str) -> None:
        """
        Load a snapshot from JSON file asynchronously.
        
        Args:
            path: The JSON file path to load from.
        """
        self.operation_active.emit(True)
        self.message_logged.emit(f"📂 Loading snapshot from: {path}")
        
        # Create and configure worker
        use_case = self._container.get_load_snapshot_use_case()
        worker = AsyncWorker(use_case.execute, path)
        
        # Connect signals
        worker.signals.result.connect(self._on_load_completed)
        worker.signals.error.connect(self._on_load_error)
        worker.signals.finished.connect(self._on_operation_finished)
        
        # Start worker
        self._threadpool.start(worker)
    
    def recreate_directory(self, snapshot: DirectorySnapshot, output_path: str) -> None:
        """
        Recreate directory structure from snapshot asynchronously.
        
        Args:
            snapshot: The snapshot to recreate from.
            output_path: The directory to recreate into.
        """
        self.operation_active.emit(True)
        self.message_logged.emit(f"🏗️ Recreating directory at: {output_path}")
        
        # Create request
        request = RecreateRequest(
            snapshot=snapshot,
            output_path=output_path,
            progress_callback=self._on_recreate_progress,
            log_callback=self._on_recreate_log
        )
        
        # Create and configure worker
        use_case = self._container.get_recreate_directory_use_case()
        worker = AsyncWorker(use_case.execute, request)
        
        # Connect signals
        worker.signals.result.connect(lambda: self._on_recreate_completed(output_path))
        worker.signals.error.connect(self._on_recreate_error)
        worker.signals.finished.connect(self._on_operation_finished)
        
        # Start worker
        self._threadpool.start(worker)
    
    def _on_recreate_progress(self, current: int, total: int) -> None:
        """Handle recreate progress updates."""
        if total > 0:
            self.progress_max_changed.emit(total)
            self.progress_changed.emit(current)
    
    def _on_recreate_log(self, message: str) -> None:
        """Handle recreate log messages."""
        self.message_logged.emit(message)
    
    def _on_load_completed(self, snapshot: DirectorySnapshot) -> None:
        """Handle successful load completion."""
        self._current_snapshot = snapshot
        self.message_logged.emit(
            f"✅ Loaded snapshot: {snapshot.get_file_count()} files, "
            f"{snapshot.get_directory_count()} directories"
        )
        self.status_update.emit("Snapshot loaded successfully", 5000)
        self.load_completed.emit(snapshot)
    
    def _on_load_error(self, error_msg: str) -> None:
        """Handle load errors."""
        self.message_logged.emit(f"❌ Load error: {error_msg}")
        self.status_update.emit("Load failed", 5000)
    
    def _on_recreate_completed(self, output_path: str) -> None:
        """Handle successful recreate completion."""
        self.message_logged.emit(f"✅ Directory recreated at: {output_path}")
        self.status_update.emit("Recreation completed successfully", 5000)
    
    def _on_recreate_error(self, error_msg: str) -> None:
        """Handle recreate errors."""
        self.message_logged.emit(f"❌ Recreation error: {error_msg}")
        self.status_update.emit("Recreation failed", 5000)
    
    def _on_operation_finished(self) -> None:
        """Handle operation completion (success or failure)."""
        self.operation_active.emit(False)
