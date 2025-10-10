import traceback
from PySide6.QtCore import QObject, Signal, QRunnable, Slot

# ------------------------ Worker Signals ------------------------#
class WorkerSignals(QObject):
    """Defines signals available from a running worker thread."""
    error = Signal(str)         # Emitted when an error occurs in the task
    finished = Signal()         # Emitted when the task is finished (success or error)
    log_message = Signal(str)   # Emitted for logging messages during the task
    progress_update = Signal(int) # Emitted with the current progress percentage (0-100)
    progress_max = Signal(int)    # Emitted with the maximum value for progress (usually total files)


# ------------------------ Worker ------------------------#
class Worker(QRunnable):
    """
    Runnable worker task for executing long operations (like scanning/recreating)
    in a separate thread to avoid blocking the main GUI thread.
    """
    def __init__(self, task_func):
        """
        Initializes the Worker.

        Args:
            task_func (callable): The function to execute in the background.
                                  This function MUST accept two arguments:
                                  progress_callback(current, total) and
                                  file_log_callback(message).
        """
        super().__init__()
        self.task_func = task_func
        self.signals = WorkerSignals() # Holds signals to communicate with the main thread

    @Slot() # Make run method a slot
    def run(self):
        """Executes the task function and handles signals."""
        try:
            # --- Define internal callback functions ---
            # These functions will emit signals back to the main thread (ViewModel)

            # Callback for progress updates from the model
            def progress_update_callback(current, total):
                # Set max value first (important for percentage calculation)
                # Ensure total is at least 1 to avoid division by zero
                safe_total = total if total > 0 else 1
                self.signals.progress_max.emit(safe_total)
                # Calculate percentage
                percentage = int((current / safe_total) * 100)
                self.signals.progress_update.emit(percentage)


            # Callback for log messages from the model
            def log_message_callback(message):
                self.signals.log_message.emit(message)

            # --- Execute the provided task function ---
            # Pass the internal callbacks to the task function
            self.task_func(
                progress_callback=progress_update_callback,
                file_log_callback=log_message_callback
            )
        except Exception as e:
            # --- Error Handling ---
            # Capture any exception during task execution
            error_info = f"{type(e).__name__}: {str(e)}"
            # Emit the error message via the log signal for the main log area
            self.signals.log_message.emit(f"❌ Worker Error: {error_info}")
            # Emit the specific error signal for status bar/dialogs
            self.signals.error.emit(error_info)
            # Print full traceback to console for debugging purposes
            traceback.print_exc()
        finally:
            # --- Cleanup ---
            # Always emit the finished signal, regardless of success or error
            self.signals.finished.emit()