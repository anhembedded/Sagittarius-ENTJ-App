"""Worker signals for async operations."""

from PySide6.QtCore import QObject, Signal


class WorkerSignals(QObject):
    """Defines signals available from a running worker thread."""
    
    error = Signal(str)          # Emitted when an error occurs in the task
    error_with_exception = Signal(str, object)  # Emitted with error message and exception object
    finished = Signal()          # Emitted when the task is finished (success or error)
    log_message = Signal(str)    # Emitted for logging messages during the task
    progress_update = Signal(int) # Emitted with the current progress value (current files)
    progress_max = Signal(int)    # Emitted with the maximum value for progress (total files)
    result = Signal(object)      # Emitted with the result of the operation
