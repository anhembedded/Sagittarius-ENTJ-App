import os
import base64
import json
import sys
import traceback # For detailed error logging in worker
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QListWidget, QListWidgetItem,
                             QTextEdit, QFileDialog, QMessageBox, QGroupBox,
                             QLabel, QFormLayout, QProgressBar, QStatusBar, QStyle) # Added QProgressBar, QStatusBar, QStyle
from PySide6.QtCore import (Qt, QObject, Signal, QRunnable, QThreadPool, QSettings, QTimer, Slot) # Added QTimer, Slot
from PySide6.QtGui import QIcon # Added QIcon


# ------------------------ Model ------------------------#
class Model:
    """Handles data storage, file scanning, and recreation."""
    def __init__(self):
        """Initializes the model with an empty database."""
        self.database = {
            'directories': [],
            'files': []
        }

    # Modified to accept progress_callback and file_log_callback
    def scan_directory(self, root_dir, extensions, progress_callback=None, file_log_callback=None):
        """
        Scans the directory, encodes files, reports progress, and logs files.

        Args:
            root_dir (str): The directory to scan.
            extensions (list): List of file extensions (lowercase) to include.
            progress_callback (callable, optional): Reports progress (current, total).
            file_log_callback (callable, optional): Logs individual file actions.
        """
        # Reset database for a new scan
        self.database = {
            'directories': [],
            'files': []
        }
        # Ensure extensions are lowercase for case-insensitive matching
        extensions = [ext.lower() for ext in extensions]

        if file_log_callback:
            file_log_callback(f"🔍 Starting scan in: {root_dir}")

        # --- First Pass: Count matching files for progress bar ---
        total_files_to_process = 0
        if progress_callback:
            if file_log_callback:
                file_log_callback("⏳ Counting files for progress...")
            try:
                for _, _, filenames in os.walk(root_dir):
                    for filename in filenames:
                        _ , ext_part = os.path.splitext(filename)
                        if ext_part and ext_part.lower() in extensions:
                            total_files_to_process += 1
            except OSError as e:
                 if file_log_callback:
                    file_log_callback(f"❌ Error during file counting: {e}")
                 raise # Re-raise the error to be caught by the worker
            progress_callback(0, total_files_to_process) # Initialize progress
            if file_log_callback:
                file_log_callback(f"🔢 Found {total_files_to_process} files matching extensions.")
        # --- End First Pass ---


        # --- Second Pass: Collect directories and process files ---
        processed_files_count = 0
        try:
            # Collect directories first to ensure structure exists if needed later
            for dirpath, _, _ in os.walk(root_dir):
                # Calculate relative path from the root directory
                rel_dir = os.path.relpath(dirpath, root_dir)
                # Store only non-root relative paths
                if rel_dir and rel_dir != '.':
                    # Normalize path separators for consistency
                    self.database['directories'].append(rel_dir.replace(os.sep, '/'))

            # Collect and encode files
            for dirpath, _, filenames in os.walk(root_dir):
                for filename in filenames:
                    _ , ext_part = os.path.splitext(filename)
                    # Skip files without extensions
                    if not ext_part: continue
                    ext = ext_part.lower()

                    # Process only files with matching extensions
                    if ext in extensions:
                        file_path = os.path.join(dirpath, filename)
                        # Calculate relative path for storage
                        rel_path = os.path.relpath(file_path, root_dir).replace(os.sep, '/')
                        try:
                            # Read file content as binary
                            with open(file_path, 'rb') as f:
                                content = f.read()
                            # Encode content in Base64
                            content_b64 = base64.b64encode(content).decode('utf-8')
                            # Store file info in the database
                            self.database['files'].append({
                                'path': rel_path,
                                'content_base64': content_b64
                            })
                            processed_files_count += 1
                            if file_log_callback:
                                file_log_callback(f"  [Encode] -> {rel_path}")
                            if progress_callback:
                                # Update progress after successful processing
                                progress_callback(processed_files_count, total_files_to_process)

                        except Exception as e:
                            # Log errors encountered during file reading/encoding
                            if file_log_callback:
                                file_log_callback(f"  [Error reading {rel_path}] -> {e}")
                            # Decide if errors should count towards progress (currently they don't)

        except OSError as e:
            if file_log_callback:
                file_log_callback(f"❌ Error during directory walk: {e}")
            raise # Re-raise the error

        if file_log_callback:
            file_log_callback(f"📊 Scan complete. Found {len(self.database['directories'])} subdirs and encoded {processed_files_count} files.")
        # --- End Second Pass ---

    def save_database(self, json_path):
        """Saves the current database to a JSON file."""
        try:
            # Ensure the directory for the JSON file exists
            os.makedirs(os.path.dirname(json_path), exist_ok=True)
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(self.database, f, indent=2)
        except OSError as e:
            # Log or raise error if saving fails
            print(f"Error saving database to {json_path}: {e}") # Simple print, consider logging
            raise

    def load_database(self, json_path):
        """Loads the database from a JSON file."""
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                self.database = json.load(f)
        except FileNotFoundError:
            print(f"Error: Database file not found at {json_path}")
            self.database = {'directories': [], 'files': []} # Reset database
            raise
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON from {json_path}: {e}")
            self.database = {'directories': [], 'files': []} # Reset database
            raise
        except Exception as e:
            print(f"An unexpected error occurred loading database: {e}")
            self.database = {'directories': [], 'files': []} # Reset database
            raise


    # Modified to accept progress_callback and file_log_callback
    def recreate_from_database(self, output_dir, progress_callback=None, file_log_callback=None):
        """
        Recreates directory structure and files from the loaded database.

        Args:
            output_dir (str): The root directory to recreate into.
            progress_callback (callable, optional): Reports progress (current, total).
            file_log_callback (callable, optional): Logs individual file actions.
        """
        if file_log_callback:
            file_log_callback(f"🏗️ Starting recreation in: {output_dir}")

        # --- Setup Progress ---
        files_to_recreate = self.database.get('files', [])
        total_files_to_process = len(files_to_recreate)
        processed_files_count = 0
        if progress_callback:
            progress_callback(0, total_files_to_process) # Initialize progress
        # --- End Setup Progress ---


        # --- Create directories ---
        dir_count = 0
        try:
            # Ensure the main output directory exists
            os.makedirs(output_dir, exist_ok=True)
            # Create all subdirectories listed in the database
            for rel_dir in self.database.get('directories', []):
                # Skip empty or '.' relative paths
                if rel_dir and rel_dir != '.':
                    try:
                        # Construct full path and create directory
                        dir_path = os.path.join(output_dir, rel_dir.replace('/', os.sep)) # Use OS-specific separator
                        os.makedirs(dir_path, exist_ok=True)
                        dir_count += 1
                    except Exception as e:
                        # Log errors during directory creation
                        if file_log_callback:
                            file_log_callback(f"  [Error creating dir {rel_dir}] -> {e}")
        except OSError as e:
             if file_log_callback:
                file_log_callback(f"❌ Error creating base output directory {output_dir}: {e}")
             raise
        # --- End Create directories ---


        # --- Create files ---
        for file_info in files_to_recreate:
            rel_path = file_info.get('path')
            content_b64 = file_info.get('content_base64')

            # Validate file information
            if not rel_path or content_b64 is None:
                if file_log_callback:
                    file_log_callback("  [Skipping file] -> Missing path or content in database.")
                # Decide if skipped files affect progress total (currently they don't reduce total)
                continue

            # Construct full file path
            file_path = os.path.join(output_dir, rel_path.replace('/', os.sep)) # Use OS-specific separator
            file_dir = os.path.dirname(file_path)

            # Ensure the file's directory exists
            if file_dir:
                try:
                    os.makedirs(file_dir, exist_ok=True)
                except Exception as e:
                    if file_log_callback:
                        file_log_callback(f"  [Error creating dir for file {rel_path}] -> {e}")
                    # Skip this file if its directory cannot be created
                    continue

            # Decode and write the file content
            try:
                content = base64.b64decode(content_b64)
                with open(file_path, 'wb') as f:
                    f.write(content)
                processed_files_count += 1
                if file_log_callback:
                    file_log_callback(f"  [Decode] -> {rel_path}")
                if progress_callback:
                    # Update progress after successful file writing
                    progress_callback(processed_files_count, total_files_to_process)
            except Exception as e:
                if file_log_callback:
                    file_log_callback(f"  [Error writing {rel_path}] -> {e}")
                # Decide if errors should count towards progress (currently they don't)

        if file_log_callback:
            log_msg = f"✅ Recreation complete. Created {dir_count} dirs, processed {processed_files_count}/{total_files_to_process} files."
            file_log_callback(log_msg)
        # --- End Create files ---


# ------------------------ Worker Signals ------------------------#
class WorkerSignals(QObject):
    """Defines signals available from a running worker thread."""
    error = Signal(str)         # Emitted when an error occurs in the task
    finished = Signal()         # Emitted when the task is finished (success or error)
    log_message = Signal(str)   # Emitted for logging messages during the task
    progress_update = Signal(int) # Emitted with the current progress percentage (0-100)
    progress_max = Signal(int)    # Emitted with the maximum value for progress (usually total files)


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

    # --- Settings Keys ---
    SETTINGS_EXTENSIONS = "extensions"
    SETTINGS_COPY_SOURCE_DIR = "paths/copySourceDir"
    SETTINGS_COPY_JSON_PATH = "paths/copyJsonPath"
    SETTINGS_PASTE_JSON_PATH = "paths/pasteJsonPath"
    SETTINGS_PASTE_OUTPUT_DIR = "paths/pasteOutputDir"

    def __init__(self, model):
        """Initializes the ViewModel."""
        super().__init__()
        self.model = model
        self.threadpool = QThreadPool()
        # Use a unique name for settings to avoid conflicts
        self.settings = QSettings("HoangAnhTran", "DirSnapshotApp_v3_Fixed")

        # --- Load persistent settings ---
        default_extensions = ['.txt', '.py', '.md', '.cpp', '.h'] # Added C++ extensions
        # Use .value() with defaultValue for robustness
        self._extensions = self.settings.value(self.SETTINGS_EXTENSIONS, defaultValue=default_extensions, type=list)
        self._copy_source_dir = self.settings.value(self.SETTINGS_COPY_SOURCE_DIR, defaultValue='', type=str)
        self._copy_json_path = self.settings.value(self.SETTINGS_COPY_JSON_PATH, defaultValue='', type=str)
        self._paste_json_path = self.settings.value(self.SETTINGS_PASTE_JSON_PATH, defaultValue='', type=str)
        self._paste_output_dir = self.settings.value(self.SETTINGS_PASTE_OUTPUT_DIR, defaultValue='', type=str)

        # Emit initial status message
        self.status_update.emit("Application loaded settings.", 3000)


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


# ------------------------ View ------------------------#
class View(QWidget):
    """The main application window (GUI)."""
    def __init__(self, viewmodel):
        """Initializes the View."""
        super().__init__()
        self.viewmodel = viewmodel
        self.init_ui()       # Create UI elements
        self.apply_styles()  # Apply CSS-like styling
        self.connect_signals() # Connect UI elements to ViewModel and vice-versa
        self.load_initial_data() # Populate UI with initial values from ViewModel
        self.setMinimumSize(800, 700) # Adjusted size for better layout

    def init_ui(self):
        """Creates and arranges all UI widgets."""
        self.setWindowTitle("✨ Sagittarius-ENTJ-App ✨ (Anh.Embedded@gmail.com)") # Updated title
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15) # Add spacing between main sections

        # --- Icons (using standard Qt icons) ---
        self.icon_folder_open = self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon)
        self.icon_save = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton)
        self.icon_open = self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton)
        self.icon_add = self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder) # Using 'New Folder' icon for Add
        self.icon_remove = self.style().standardIcon(QStyle.StandardPixmap.SP_TrashIcon)
        self.icon_copy = self.style().standardIcon(QStyle.StandardPixmap.SP_CommandLink) # Using CommandLink for Copy action
        self.icon_paste = self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowRight) # Using ArrowRight for Paste action


        # --- Copy Section ---
        copy_group = QGroupBox("1. Snapshot Source Directory (Copy)")
        copy_layout = QFormLayout()
        copy_layout.setSpacing(10) # Spacing within the form

        self.copy_source_edit = QLineEdit()
        self.copy_source_edit.setPlaceholderText("Select directory to snapshot...")
        copy_layout.addRow("Source Directory:", self._create_browse_row(
            self.copy_source_edit, self._browse_copy_source, icon=self.icon_folder_open, tooltip="Select Source Directory"))

        self.copy_json_edit = QLineEdit()
        self.copy_json_edit.setPlaceholderText("Select location to save snapshot JSON...")
        copy_layout.addRow("Snapshot JSON File:", self._create_browse_row(
            self.copy_json_edit, self._browse_copy_json_save, icon=self.icon_save, tooltip="Select Snapshot Save Location"))

        # Extensions UI
        self.ext_list = QListWidget()
        self.ext_list.setToolTip("Files with these extensions will be included in the snapshot.")
        self.ext_list.setSelectionMode(QListWidget.SelectionMode.ExtendedSelection) # Allow multi-select
        copy_layout.addRow("Include Extensions:", self.ext_list)

        ext_control_layout = QHBoxLayout()
        self.ext_edit = QLineEdit()
        self.ext_edit.setPlaceholderText(".ext (e.g., .txt, .py)")
        self.ext_edit.setToolTip("Enter extension with leading dot and press Add or Enter.")
        ext_control_layout.addWidget(self.ext_edit, 1) # Stretch line edit

        self.add_ext_btn = QPushButton("Add")
        self.add_ext_btn.setIcon(self.icon_add)
        self.add_ext_btn.setToolTip("Add the extension typed above.")
        ext_control_layout.addWidget(self.add_ext_btn)

        self.remove_ext_btn = QPushButton("Remove")
        self.remove_ext_btn.setIcon(self.icon_remove)
        self.remove_ext_btn.setToolTip("Remove selected extensions from the list.")
        ext_control_layout.addWidget(self.remove_ext_btn)
        copy_layout.addRow(ext_control_layout) # Add the HBox layout as a row

        self.copy_btn = QPushButton("Create Snapshot")
        self.copy_btn.setIcon(self.icon_copy)
        self.copy_btn.setToolTip("Scan source directory and save snapshot to JSON.")
        copy_layout.addRow(self.copy_btn) # Add button spanning columns

        copy_group.setLayout(copy_layout)
        main_layout.addWidget(copy_group)
        # --- End Copy Section ---


        # --- Paste Section ---
        paste_group = QGroupBox("2. Recreate from Snapshot (Paste)")
        paste_layout = QFormLayout()
        paste_layout.setSpacing(10)

        self.paste_json_edit = QLineEdit()
        self.paste_json_edit.setPlaceholderText("Select snapshot JSON file to load...")
        paste_layout.addRow("Snapshot JSON File:", self._create_browse_row(
            self.paste_json_edit, self._browse_paste_json_open, icon=self.icon_open, tooltip="Select Snapshot File to Load"))

        self.paste_output_edit = QLineEdit()
        self.paste_output_edit.setPlaceholderText("Select directory to recreate files into...")
        paste_layout.addRow("Output Directory:", self._create_browse_row(
            self.paste_output_edit, self._browse_paste_output, icon=self.icon_folder_open, tooltip="Select Output Directory"))

        self.paste_btn = QPushButton("Recreate Files")
        self.paste_btn.setIcon(self.icon_paste)
        self.paste_btn.setToolTip("Recreate directory structure and files from the selected snapshot JSON.")
        paste_layout.addRow(self.paste_btn) # Add button spanning columns

        paste_group.setLayout(paste_layout)
        main_layout.addWidget(paste_group)
        # --- End Paste Section ---


        # --- Progress Bar ---
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setVisible(False) # Initially hidden
        self.progress_bar.setRange(0, 100)  # Standard percentage range
        self.progress_bar.setValue(0)
        main_layout.addWidget(self.progress_bar)
        # --- End Progress Bar ---


        # --- Log Section ---
        log_group = QGroupBox("Operation Log")
        log_layout = QVBoxLayout()
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth) # Wrap long lines
        log_layout.addWidget(self.log)
        log_group.setLayout(log_layout)
        # Add stretch factor so log area takes up remaining vertical space
        main_layout.addWidget(log_group, 1)
        # --- End Log Section ---


        # --- Status Bar ---
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False) # Optional: disable resize grip
        main_layout.addWidget(self.status_bar)
        # --- End Status Bar ---

    def apply_styles(self):
        """Apply custom stylesheets for a more modern look."""
        # Color Palette (adjust as desired)
        primary_color = "#007ACC" # Brighter Blue
        secondary_color = "#6c757d" # Gray
        success_color = "#28a745" # Green
        info_color = "#17a2b8" # Teal
        warning_color = "#ffc107" # Yellow
        danger_color = "#dc3545" # Red
        bg_color = "#f8f9fa" # Light gray background
        text_color = "#212529" # Dark text
        border_color = "#ced4da"
        group_bg_color = "#ffffff" # White background for group boxes

        self.setStyleSheet(f"""
            QWidget {{
                font-family: Segoe UI, Arial, sans-serif;
                font-size: 10pt;
                background-color: {bg_color};
                color: {text_color};
            }}
            QGroupBox {{
                border: 1px solid {border_color};
                border-radius: 6px; /* Slightly more rounded */
                margin-top: 12px; /* Space for title */
                background-color: {group_bg_color};
                padding: 10px; /* Padding inside groupbox */
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 4px 8px; /* Adjusted padding */
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {primary_color}, stop:1 #0056b3);
                color: white;
                border-radius: 4px;
                margin-left: 10px; /* Indent title slightly */
            }}
            QLineEdit, QTextEdit, QListWidget {{
                border: 1px solid {border_color};
                border-radius: 4px; /* Consistent rounding */
                padding: 5px; /* Slightly more padding */
                background-color: white;
            }}
            QLineEdit:focus, QTextEdit:focus, QListWidget:focus {{
                border-color: {primary_color}; /* Highlight focus */
            }}
            QListWidget::item {{
                 padding: 3px; /* Spacing for list items */
            }}
            QListWidget::item:selected {{
                background-color: {primary_color};
                color: white;
            }}
            QPushButton {{
                border: 1px solid {secondary_color};
                border-radius: 4px;
                padding: 6px 15px; /* More horizontal padding */
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #ffffff, stop:1 #e9ecef); /* Lighter gradient */
                min-width: 90px; /* Minimum width */
                icon-size: 16px; /* Ensure icons aren't too large */
            }}
            QPushButton:hover {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #f8f9fa, stop:1 #d3d9df); /* Slightly darker hover */
                border-color: #5a6268;
            }}
            QPushButton:pressed {{
                background-color: #d3d9df; /* Pressed state */
                border-color: #5a6268;
            }}
            QPushButton:disabled {{ /* Style for disabled state */
                 background-color: #e9ecef;
                 color: #6c757d;
                 border-color: {border_color};
            }}

            /* Specific button styles using objectName */
            QPushButton#CopyButton {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {success_color}, stop:1 #1e7e34);
                color: white;
                border-color: #1c7430;
            }}
            QPushButton#CopyButton:hover {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #34c759, stop:1 #218838);
                border-color: #1e7e34;
            }}
             QPushButton#CopyButton:disabled {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #a1dca7, stop:1 #6ba77c);
                border-color: #90c497;
                color: #f0f0f0;
            }}

            QPushButton#PasteButton {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 {info_color}, stop:1 #117a8b);
                color: white;
                border-color: #10707f;
            }}
            QPushButton#PasteButton:hover {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #17a2b8, stop:1 #138496);
                border-color: #117a8b;
            }}
             QPushButton#PasteButton:disabled {{
                 background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #97d9e3, stop:1 #67a1aa);
                 border-color: #8ac9d3;
                 color: #f0f0f0;
            }}

            QProgressBar {{
                border: 1px solid {border_color};
                border-radius: 4px;
                text-align: center;
                background-color: white;
                color: {text_color}; /* Ensure text is visible */
            }}
            QProgressBar::chunk {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {success_color}, stop:1 #a1f0a1); /* Green gradient chunk */
                border-radius: 3px; /* Slightly smaller radius for chunk */
                margin: 1px; /* Small margin around the chunk */
            }}
            QStatusBar {{
                background-color: #e9ecef;
                color: {secondary_color};
                font-size: 9pt; /* Slightly smaller font for status bar */
            }}
            QToolTip {{ /* Style tooltips */
                background-color: #343a40;
                color: white;
                border: 1px solid #343a40;
                padding: 4px;
                border-radius: 3px;
            }}
        """)
        # Set object names for specific styling and easier identification
        self.copy_btn.setObjectName("CopyButton")
        self.paste_btn.setObjectName("PasteButton")
        self.add_ext_btn.setObjectName("AddExtButton")
        self.remove_ext_btn.setObjectName("RemoveExtButton")


    def _create_browse_row(self, line_edit, handler, icon=None, tooltip="Browse..."):
        """Helper to create a row with a LineEdit and an icon Browse button."""
        row_widget = QWidget() # Container widget for the row
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0,0,0,0) # No internal margins for the HBox
        row_layout.setSpacing(5) # Spacing between line edit and button

        row_layout.addWidget(line_edit, 1) # LineEdit takes available horizontal space

        btn = QPushButton()
        if icon:
            btn.setIcon(icon)
        else:
            btn.setText("...") # Fallback text if no icon
        btn.setToolTip(tooltip) # Set tooltip for the button
        btn.setFixedSize(btn.iconSize().width() + 18, btn.iconSize().height() + 10) # Adjust size for icon padding
        btn.clicked.connect(handler)
        row_layout.addWidget(btn)

        return row_widget # Return the container widget


    def connect_signals(self):
        """Connect signals from UI elements to ViewModel slots and vice-versa."""
        # --- View -> ViewModel ---
        # Connect textChanged signals to the NEW explicit ViewModel slots
        self.copy_source_edit.textChanged.connect(self.viewmodel.set_copy_source_dir)
        self.copy_json_edit.textChanged.connect(self.viewmodel.set_copy_json_path)
        self.paste_json_edit.textChanged.connect(self.viewmodel.set_paste_json_path)
        self.paste_output_edit.textChanged.connect(self.viewmodel.set_paste_output_dir)

        # Connect button clicks to ViewModel actions
        self.copy_btn.clicked.connect(self.viewmodel.perform_copy)
        self.paste_btn.clicked.connect(self.viewmodel.perform_paste)
        self.add_ext_btn.clicked.connect(self._add_extension)
        self.remove_ext_btn.clicked.connect(self._remove_extensions)

        # Handle Enter key press in extension edit field for convenience
        self.ext_edit.returnPressed.connect(self._add_extension)

        # --- ViewModel -> View ---
        # Connect ViewModel signals to View update slots
        self.viewmodel.message_logged.connect(self._log_message) # Use custom slot for formatting
        self.viewmodel.status_update.connect(self._show_status_message)
        self.viewmodel.extensions_changed.connect(self._update_extensions_list)
        self.viewmodel.progress_changed.connect(self.progress_bar.setValue)
        self.viewmodel.progress_max_changed.connect(self.progress_bar.setMaximum)
        self.viewmodel.operation_active.connect(self._set_operation_active_state) # Handle UI enabling/disabling


    def load_initial_data(self):
        """Populates the UI fields with data from the ViewModel on startup."""
        # Use setText which will trigger textChanged -> ViewModel update via slots
        self.copy_source_edit.setText(self.viewmodel.copy_source_dir)
        self.copy_json_edit.setText(self.viewmodel.copy_json_path)
        self.paste_json_edit.setText(self.viewmodel.paste_json_path)
        self.paste_output_edit.setText(self.viewmodel.paste_output_dir)
        # Update the extensions list display
        self._update_extensions_list(self.viewmodel.extensions)
        # Set initial status bar message
        self.status_bar.showMessage("Ready.", 2000)


    # --- Browse Handlers ---
    # These methods open file/directory dialogs and update the corresponding LineEdits.
    def _browse_copy_source(self):
        """Opens a dialog to select the source directory for copying."""
        # Start browsing from the current path or user's home directory
        start_dir = self.viewmodel.copy_source_dir or os.path.expanduser("~")
        directory = QFileDialog.getExistingDirectory(self, "Select Source Directory", start_dir)
        if directory:
            # Update the LineEdit; textChanged signal will update the ViewModel
            self.copy_source_edit.setText(directory)

    def _browse_copy_json_save(self):
        """Opens a dialog to select the save location for the snapshot JSON."""
        # Suggest a default filename and location
        start_path = self.viewmodel.copy_json_path or os.path.join(os.path.expanduser("~"), "snapshot.json")
        path, _ = QFileDialog.getSaveFileName(self, "Save Snapshot File", start_path, "JSON Files (*.json)")
        if path:
            # Ensure the file has a .json extension
            if not path.lower().endswith('.json'):
                path += '.json'
            # Update the LineEdit; textChanged signal updates ViewModel
            self.copy_json_edit.setText(path)

    def _browse_paste_json_open(self):
        """Opens a dialog to select the snapshot JSON file to load."""
        start_path = self.viewmodel.paste_json_path or os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(self, "Select Snapshot File", start_path, "JSON Files (*.json)")
        if path:
            # Update the LineEdit; textChanged signal updates ViewModel
            self.paste_json_edit.setText(path)

    def _browse_paste_output(self):
        """Opens a dialog to select the output directory for recreation."""
        start_dir = self.viewmodel.paste_output_dir or os.path.expanduser("~")
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", start_dir)
        if directory:
            # Update the LineEdit; textChanged signal updates ViewModel
            self.paste_output_edit.setText(directory)
    # --- End Browse Handlers ---


    # --- Extension Handlers ---
    # Methods for adding and removing extensions from the list.
    def _add_extension(self):
        """Adds the extension from the input field to the ViewModel."""
        ext = self.ext_edit.text().strip()
        if not ext: return # Ignore empty input

        # Basic validation: must start with '.'
        if not ext.startswith('.'):
            QMessageBox.warning(self, "Invalid Extension", "Extension must start with a dot (e.g., .txt, .py)")
            return

        # Call ViewModel method to add the extension
        self.viewmodel.add_extension(ext.lower()) # Add in lowercase
        self.ext_edit.clear() # Clear input field after adding

    def _remove_extensions(self):
        """Removes selected extensions from the list via the ViewModel."""
        selected_items = self.ext_list.selectedItems()
        if not selected_items:
            self._show_status_message("No extensions selected to remove.", 2000)
            return

        # Confirm removal with the user
        reply = QMessageBox.question(self, 'Confirm Removal',
                                       f"Remove {len(selected_items)} selected extension(s)?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                       QMessageBox.StandardButton.No) # Default to No

        if reply == QMessageBox.StandardButton.Yes:
            for item in selected_items:
                # Call ViewModel method to remove each selected extension
                self.viewmodel.remove_extension(item.text())

    @Slot(list) # Explicitly define as slot receiving a list
    def _update_extensions_list(self, extensions):
        """Updates the QListWidget with the current list of extensions."""
        self.ext_list.clear() # Remove existing items
        self.ext_list.addItems(sorted(extensions)) # Add sorted items
    # --- End Extension Handlers ---

    # --- UI Update Slots ---

    @Slot(str)
    def _log_message(self, message):
        """Appends a message to the log QTextEdit, ensuring it scrolls to the bottom."""
        self.log.append(message)
        # Optional: Add timestamp or formatting here if desired
        # self.log.append(f"[{datetime.datetime.now():%H:%M:%S}] {message}")
        self.log.ensureCursorVisible() # Auto-scroll to the latest message

    @Slot(str, int)
    def _show_status_message(self, message, timeout):
        """Shows a message in the status bar for a specified duration (milliseconds)."""
        self.status_bar.showMessage(message, timeout)

    @Slot(bool)
    def _set_operation_active_state(self, active):
        """Enables/disables UI elements based on whether an operation is running."""
        self.progress_bar.setVisible(active)
        # Disable buttons and input fields during operation
        self.copy_source_edit.setEnabled(not active)
        self.copy_json_edit.setEnabled(not active)
        # Find browse buttons associated with line edits and disable them
        # (This assumes the browse button is the sibling widget in the layout)
        self.copy_source_edit.parentWidget().findChild(QPushButton).setEnabled(not active)
        self.copy_json_edit.parentWidget().findChild(QPushButton).setEnabled(not active)

        self.ext_list.setEnabled(not active)
        self.ext_edit.setEnabled(not active)
        self.add_ext_btn.setEnabled(not active)
        self.remove_ext_btn.setEnabled(not active)
        self.copy_btn.setEnabled(not active)

        self.paste_json_edit.setEnabled(not active)
        self.paste_output_edit.setEnabled(not active)
        self.paste_json_edit.parentWidget().findChild(QPushButton).setEnabled(not active)
        self.paste_output_edit.parentWidget().findChild(QPushButton).setEnabled(not active)
        self.paste_btn.setEnabled(not active)

        # Change cursor to busy if active, otherwise default
        if active:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        else:
            QApplication.restoreOverrideCursor()

    # --- End UI Update Slots ---

    def closeEvent(self, event):
        """Handle the window close event."""
        # Optional: Add confirmation dialog or cleanup here if needed
        # reply = QMessageBox.question(self, 'Confirm Exit', 'Are you sure you want to exit?',
        #                              QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        #                              QMessageBox.StandardButton.No)
        # if reply == QMessageBox.StandardButton.Yes:
        #     # Clean up threads if necessary (though QThreadPool usually manages this)
        #     # self.viewmodel.threadpool.waitForDone()
        #     event.accept()
        # else:
        #     event.ignore()
        # For now, just accept the close event
        event.accept()


# ------------------------ Main Application Entry Point ------------------------#
def main():
    """Sets up and runs the Qt application."""
    # Set application details used by QSettings
    QApplication.setOrganizationName("HoangAnhTran") # Use your name or company
    QApplication.setApplicationName("DirSnapshotApp_v3_Fixed") # Match ViewModel QSettings

    # Enable High DPI scaling for better visuals on modern displays
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)

    # --- Instantiate MVC components ---
    model = Model()
    viewmodel = ViewModel(model)
    view = View(viewmodel)
    view.show() # Display the main window

    # --- Start the Qt event loop ---
    sys.exit(app.exec())


if __name__ == '__main__':
    main() # Run the main function when the script is executed
