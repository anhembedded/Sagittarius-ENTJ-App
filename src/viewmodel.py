import os
from PySide6.QtCore import QObject, Signal, QThreadPool, QSettings, QTimer, Slot
from PySide6.QtWidgets import QMessageBox

from src.model import Model
from src.worker import Worker


# ------------------------ ViewModel ------------------------#
class ViewModel(QObject):
    """Manages application state, logic, and communication between Model and View."""
    # --- Signals for View updates ---
    message_logged = Signal(str)        # Signal to send messages to the main log view
    status_update = Signal(str, int)    # Signal to update the status bar (message, timeout_ms)
    extensions_changed = Signal(list)   # Signal when the list of extensions is modified
    progress_changed = Signal(int)      # Signal to update the progress bar's value
    progress_max_changed = Signal(int)  # Signal to update the progress bar's maximum
    operation_active = Signal(bool)     # Signal to show/hide the progress bar and disable buttons
    theme_changed = Signal(str)         # Signal when the theme is changed

    # --- Settings Keys ---
    SETTINGS_THEME = "theme"
    SETTINGS_EXTENSIONS = "extensions"
    SETTINGS_COPY_SOURCE_DIR = "paths/copySourceDir"
    SETTINGS_COPY_JSON_PATH = "paths/copyJsonPath"
    SETTINGS_PASTE_JSON_PATH = "paths/pasteJsonPath"
    SETTINGS_PASTE_OUTPUT_DIR = "paths/pasteOutputDir"

    def __init__(self, model: Model):
        """Initializes the ViewModel."""
        super().__init__()
        self.model = model
        self.threadpool = QThreadPool()
        # Use a unique name for settings to avoid conflicts
        self.settings = QSettings("HoangAnhTran", "DirSnapshotApp_v3_Fixed")

        # --- Load persistent settings ---
        default_extensions = ['.txt', '.py', '.md', '.cpp', '.h'] # Added C++ extensions
        # Use .value() with defaultValue for robustness
        self._theme = self.settings.value(self.SETTINGS_THEME, defaultValue='light', type=str)
        self._extensions = self.settings.value(self.SETTINGS_EXTENSIONS, defaultValue=default_extensions, type=list)
        self._copy_source_dir = self.settings.value(self.SETTINGS_COPY_SOURCE_DIR, defaultValue='', type=str)
        self._copy_json_path = self.settings.value(self.SETTINGS_COPY_JSON_PATH, defaultValue='', type=str)
        self._paste_json_path = self.settings.value(self.SETTINGS_PASTE_JSON_PATH, defaultValue='', type=str)
        self._paste_output_dir = self.settings.value(self.SETTINGS_PASTE_OUTPUT_DIR, defaultValue='', type=str)

        # Emit initial status message
        self.status_update.emit("Application loaded settings.", 3000)


    # --- Theme Property ---
    @property
    def theme(self):
        """Gets the current theme name."""
        return self._theme

    @theme.setter
    def theme(self, value):
        """Sets the theme, saves it, and notifies the view."""
        if self._theme != value:
            self._theme = value
            self.settings.setValue(self.SETTINGS_THEME, value)
            self.theme_changed.emit(value) # Notify View
            self.status_update.emit(f"Theme changed to {value.capitalize()}.", 2000)


    # --- Properties with Persistence ---
    # Properties provide controlled access to the ViewModel's state
    # and automatically save changes to QSettings.

    @property
    def copy_source_dir(self):
        """Gets the source directory path for the copy operation."""
        return self._copy_source_dir

    # Setter for copy_source_dir property
    @copy_source_dir.setter
    def copy_source_dir(self, value):
        """Sets the source directory path and saves it to settings."""
        if self._copy_source_dir != value: # Only update if value changed
            self._copy_source_dir = value
            self.settings.setValue(self.SETTINGS_COPY_SOURCE_DIR, value)
            self.status_update.emit("Copy source path updated.", 1500) # Provide feedback

    @property
    def copy_json_path(self):
        """Gets the output JSON file path for the copy operation."""
        return self._copy_json_path

    # Setter for copy_json_path property
    @copy_json_path.setter
    def copy_json_path(self, value):
        """Sets the output JSON file path and saves it to settings."""
        if self._copy_json_path != value:
            self._copy_json_path = value
            self.settings.setValue(self.SETTINGS_COPY_JSON_PATH, value)
            self.status_update.emit("Copy JSON path updated.", 1500)

    @property
    def paste_json_path(self):
        """Gets the input JSON file path for the paste operation."""
        return self._paste_json_path

    # Setter for paste_json_path property
    @paste_json_path.setter
    def paste_json_path(self, value):
        """Sets the input JSON file path and saves it to settings."""
        if self._paste_json_path != value:
            self._paste_json_path = value
            self.settings.setValue(self.SETTINGS_PASTE_JSON_PATH, value)
            self.status_update.emit("Paste JSON path updated.", 1500)

    @property
    def paste_output_dir(self):
        """Gets the output directory path for the paste operation."""
        return self._paste_output_dir

    # Setter for paste_output_dir property
    @paste_output_dir.setter
    def paste_output_dir(self, value):
        """Sets the output directory path and saves it to settings."""
        if self._paste_output_dir != value:
            self._paste_output_dir = value
            self.settings.setValue(self.SETTINGS_PASTE_OUTPUT_DIR, value)
            self.status_update.emit("Paste output path updated.", 1500)
    # --- End Properties ---


    # --- Explicit Slots for Text Input Changes (NEW) ---
    # These slots are connected to the textChanged signals of QLineEdits
    # to ensure ViewModel properties are updated correctly.

    @Slot(str)
    def set_copy_source_dir(self, value):
        """Slot to update the copy source directory from the View."""
        self.copy_source_dir = value # Uses the property setter

    @Slot(str)
    def set_copy_json_path(self, value):
        """Slot to update the copy JSON path from the View."""
        self.copy_json_path = value # Uses the property setter

    @Slot(str)
    def set_paste_json_path(self, value):
        """Slot to update the paste JSON path from the View."""
        self.paste_json_path = value # Uses the property setter

    @Slot(str)
    def set_paste_output_dir(self, value):
        """Slot to update the paste output directory from the View."""
        self.paste_output_dir = value # Uses the property setter
    # --- End Explicit Slots ---


    # --- Extensions management ---
    @property
    def extensions(self):
        """Gets a copy of the current list of extensions."""
        # Return a copy to prevent external modification
        return self._extensions.copy()

    def add_extension(self, ext):
        """Adds a new extension to the list if valid and not present."""
        # Basic validation for the extension format
        if ext and ext.startswith('.') and ext not in self._extensions:
            self._extensions.append(ext.lower()) # Store lowercase
            self._extensions.sort() # Keep the list sorted
            self.settings.setValue(self.SETTINGS_EXTENSIONS, self._extensions) # Save changes
            self.extensions_changed.emit(self.extensions) # Notify View
            self.status_update.emit(f"Extension '{ext}' added.", 2000)
        elif ext in self._extensions:
             self.status_update.emit(f"Extension '{ext}' already exists.", 2000)
        else:
             self.status_update.emit(f"Invalid extension format: '{ext}'. Must start with '.'", 3000)


    def remove_extension(self, ext):
        """Removes an extension from the list."""
        if ext in self._extensions:
            self._extensions.remove(ext)
            # No need to sort again after removal
            self.settings.setValue(self.SETTINGS_EXTENSIONS, self._extensions) # Save changes
            self.extensions_changed.emit(self.extensions) # Notify View
            self.status_update.emit(f"Extension '{ext}' removed.", 2000)
    # --- End Extensions management ---


    # --- Actions ---
    # These methods trigger the core operations (copy/paste)
    # They perform validation and run the tasks in separate threads.

    @Slot() # Define as a slot for potential connection from View if needed
    def perform_copy(self):
        """Validates inputs and starts the copy (scan and save) operation."""
        # Validate source directory
        if not self.copy_source_dir: # Use property getter
            self.message_logged.emit("⚠️ Please select a source directory.")
            self.status_update.emit("Copy failed: No source directory selected.", 3000)
            return
        if not os.path.isdir(self.copy_source_dir):
             self.message_logged.emit(f"⚠️ Source directory not found or is not a directory: {self.copy_source_dir}")
             self.status_update.emit("Copy failed: Invalid source directory.", 3000)
             return

        # Validate output JSON path
        if not self.copy_json_path: # Use property getter
            self.message_logged.emit("⚠️ Please select an output JSON file path.")
            self.status_update.emit("Copy failed: Missing output JSON path.", 3000)
            return
        # Check if the directory for the JSON file exists (optional, save_database handles it)
        json_dir = os.path.dirname(self.copy_json_path)
        if json_dir and not os.path.isdir(json_dir):
             try:
                 os.makedirs(json_dir, exist_ok=True)
                 self.message_logged.emit(f"📁 Created directory for JSON file: {json_dir}")
             except OSError as e:
                 self.message_logged.emit(f"❌ Could not create directory for JSON file: {json_dir} - Error: {e}")
                 self.status_update.emit("Copy failed: Cannot create JSON directory.", 4000)
                 return

        # Define the task function to be run in the worker thread
        def copy_task(progress_callback, file_log_callback):
            """The actual work of scanning and saving."""
            try:
                # Pass callbacks to the model methods
                self.model.scan_directory(self.copy_source_dir, self.extensions, progress_callback, file_log_callback)
                self.model.save_database(self.copy_json_path)
                # Log success via the worker's log signal
                file_log_callback(f"💾 Snapshot database saved successfully to: {self.copy_json_path}")
            except Exception as e:
                # Log error via the worker's log signal and re-raise to trigger worker's error signal
                detailed_error = f"{type(e).__name__}: {e}"
                file_log_callback(f"❌ Error during copy operation: {detailed_error}")
                # Optionally log traceback here if needed in main log immediately
                # traceback.print_exc()
                raise # Important: re-raise the exception for the worker's error handling

        # --- Start the task ---
        self.message_logged.emit("🚀 Starting snapshot creation (copy)...")
        self.status_update.emit("Copy operation started...", 0) # Persistent status until finished/error
        self.operation_active.emit(True) # Show progress bar, disable buttons
        self._run_task(copy_task) # Run the task in a background thread

    @Slot()
    def perform_paste(self):
        """Validates inputs and starts the paste (load and recreate) operation."""
        # Validate input JSON path
        if not self.paste_json_path: # Use property getter
            self.message_logged.emit("⚠️ Please select a snapshot JSON file to load.")
            self.status_update.emit("Paste failed: No database file selected.", 3000)
            return
        if not os.path.isfile(self.paste_json_path):
             self.message_logged.emit(f"⚠️ Snapshot JSON file not found: {self.paste_json_path}")
             self.status_update.emit("Paste failed: Invalid database file.", 3000)
             return

        # Validate output directory
        if not self.paste_output_dir: # Use property getter
            self.message_logged.emit("⚠️ Please select a valid output directory.")
            self.status_update.emit("Paste failed: No output directory selected.", 3000)
            return
        if not os.path.isdir(self.paste_output_dir):
            # Ask user if they want to create the output directory
            reply = QMessageBox.question(None, "Create Directory?", # Parent can be None here
                                         f"The output directory does not exist:\n{self.paste_output_dir}\n\nDo you want to create it?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    os.makedirs(self.paste_output_dir, exist_ok=True)
                    self.message_logged.emit(f"📁 Created output directory: {self.paste_output_dir}")
                except OSError as e:
                    self.message_logged.emit(f"❌ Failed to create output directory: {e}")
                    self.status_update.emit("Paste failed: Could not create output directory.", 4000)
                    return
            else:
                self.message_logged.emit("ℹ️ Paste operation cancelled by user (output directory not created).")
                self.status_update.emit("Paste cancelled.", 3000)
                return


        # Define the task function for the worker thread
        def paste_task(progress_callback, file_log_callback):
            """The actual work of loading and recreating."""
            try:
                # Pass callbacks to the model methods
                self.model.load_database(self.paste_json_path)
                file_log_callback(f"📚 Snapshot database loaded from: {self.paste_json_path}")
                self.model.recreate_from_database(self.paste_output_dir, progress_callback, file_log_callback)
            except Exception as e:
                 # Log error via the worker's log signal and re-raise
                detailed_error = f"{type(e).__name__}: {e}"
                file_log_callback(f"❌ Error during paste operation: {detailed_error}")
                raise # Important: re-raise for worker's error handling

        # --- Start the task ---
        self.message_logged.emit("🚀 Starting directory recreation (paste)...")
        self.status_update.emit("Paste operation started...", 0) # Persistent status
        self.operation_active.emit(True) # Show progress bar, disable buttons
        self._run_task(paste_task) # Run in background thread

    def _run_task(self, task_func):
        """Creates a Worker and runs the given task function in the thread pool."""
        worker = Worker(task_func)
        # Connect worker signals to ViewModel handlers (slots)
        worker.signals.error.connect(self._handle_task_error)
        worker.signals.finished.connect(self._handle_task_finished)
        worker.signals.log_message.connect(self._handle_log_message)
        worker.signals.progress_update.connect(self._handle_progress_update)
        worker.signals.progress_max.connect(self._handle_progress_max)
        # Execute the worker task in the thread pool
        self.threadpool.start(worker)
    # --- End Actions ---


    # --- Signal Handlers (Slots) ---
    # These methods handle signals emitted by the Worker threads.

    @Slot(str)
    def _handle_log_message(self, message):
        """Receives log messages from the worker and forwards them to the View."""
        self.message_logged.emit(message)

    @Slot(int)
    def _handle_progress_update(self, value):
        """Receives progress updates (percentage) and forwards them to the View."""
        self.progress_changed.emit(value)

    @Slot(int)
    def _handle_progress_max(self, max_value):
        """Receives the maximum progress value and forwards it to the View."""
        # Ensure max value is at least 1 to avoid division by zero issues in progress bar
        self.progress_max_changed.emit(max_value if max_value > 0 else 1)


    @Slot(str)
    def _handle_task_error(self, error_message):
        """Handles errors reported by the worker."""
        # Log the specific error message received from the worker
        self.message_logged.emit(f"❌ Task Error: {error_message}")
        # Show a user-friendly error message in the status bar
        self.status_update.emit(f"Operation failed. See log for details.", 5000)
        # Re-enable UI elements and hide progress bar
        self.operation_active.emit(False)
        # Optionally reset progress bar visually after a short delay
        QTimer.singleShot(100, lambda: self.progress_changed.emit(0))


    @Slot()
    def _handle_task_finished(self):
        """Handles the finished signal from the worker (called on success or error)."""
        # Note: Success messages are now typically logged via file_log_callback within the task itself.
        # This handler mainly deals with cleanup.
        self.message_logged.emit("🏁 Task finished.") # Generic finished message
        # Status bar message might have already been set by success/error handlers,
        # but we can set a final one here if needed, or clear it.
        # self.status_update.emit("Operation finished.", 3000) # Example if needed
        self.operation_active.emit(False) # Hide progress bar, re-enable buttons
        # Reset progress bar visually after a short delay
        QTimer.singleShot(150, lambda: self.progress_changed.emit(0))
        QTimer.singleShot(150, lambda: self.progress_max_changed.emit(100)) # Reset max visually
    # --- End Signal Handlers ---