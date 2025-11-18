"""Async worker for background operations."""

import traceback
from typing import Callable, Any, Optional
from PySide6.QtCore import QRunnable, Slot

from .worker_signals import WorkerSignals


class AsyncWorker(QRunnable):
    """
    Worker thread for running background tasks.
    
    Inherits from QRunnable to handle worker thread setup, signals and wrap-up.
    """
    
    def __init__(
        self, 
        fn: Callable, 
        *args,
        **kwargs
    ):
        """
        Initialize the worker.
        
        Args:
            fn: The function to execute in the background.
            *args: Arguments to pass to the function.
            **kwargs: Keyword arguments to pass to the function.
        """
        super().__init__()
        
        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        
    @Slot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """
        try:
            result = self.fn(*self.args, **self.kwargs)
        except Exception as e:
            # Emit error with traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            self.signals.error.emit(error_msg)
        else:
            # Emit result if successful
            if result is not None:
                self.signals.result.emit(result)
        finally:
            # Always emit finished signal
            self.signals.finished.emit()
