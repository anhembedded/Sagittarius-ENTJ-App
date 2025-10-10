import os
import sys
from PySide6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QListWidget,
                             QTextEdit, QFileDialog, QMessageBox, QGroupBox,
                             QStatusBar, QStyle, QProgressBar, QComboBox, QLabel)
from PySide6.QtCore import Qt, Slot
from src.viewmodel import ViewModel


# ------------------------ View ------------------------#
class View(QWidget):
    """The main application window (GUI)."""
    def __init__(self, viewmodel: ViewModel):
        """Initializes the View."""
        super().__init__()
        self.viewmodel = viewmodel
        self.init_ui()       # Create UI elements
        # self.apply_styles() is now called from _apply_theme
        self.connect_signals() # Connect UI elements to ViewModel and vice-versa
        self.load_initial_data() # Populate UI with initial values from ViewModel
        self.setMinimumSize(800, 700) # Adjusted size for better layout

    def init_ui(self):
        """Creates and arranges all UI widgets."""
        self.setWindowTitle("✨ Sagittarius-ENTJ-App ✨ (Anh.Embedded@gmail.com)") # Updated title
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15) # Add spacing between main sections

        # --- Header with Theme Switcher ---
        header_layout = QHBoxLayout()
        header_layout.addStretch(1) # Pushes the theme switcher to the right
        header_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark"])
        self.theme_combo.setToolTip("Change the application's visual theme.")
        header_layout.addWidget(self.theme_combo)
        main_layout.addLayout(header_layout)

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

    def _load_theme(self, theme_name):
        """Loads the stylesheet from a .qss file in the themes directory."""
        # Determine the base path (works for both normal execution and PyInstaller)
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        theme_path = os.path.join(base_path, 'themes', f'{theme_name}.qss')
        try:
            with open(theme_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: Theme file not found at '{theme_path}'.")
            return "" # Return empty string if theme not found

    @Slot(str)
    def _apply_theme(self, theme_name):
        """Applies the selected theme to the application."""
        stylesheet = self._load_theme(theme_name)
        self.setStyleSheet(stylesheet)
        # Set object names for specific styling after applying the stylesheet
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
        self.theme_combo.currentTextChanged.connect(self.viewmodel.set_theme)

        # --- ViewModel -> View ---
        # Connect ViewModel signals to View update slots
        self.viewmodel.message_logged.connect(self._log_message) # Use custom slot for formatting
        self.viewmodel.status_update.connect(self._show_status_message)
        self.viewmodel.extensions_changed.connect(self._update_extensions_list)
        self.viewmodel.progress_changed.connect(self.progress_bar.setValue)
        self.viewmodel.progress_max_changed.connect(self.progress_bar.setMaximum)
        self.viewmodel.operation_active.connect(self._set_operation_active_state) # Handle UI enabling/disabling
        self.viewmodel.theme_changed.connect(self._apply_theme)


    def load_initial_data(self):
        """Populates the UI fields with data from the ViewModel on startup."""
        # Use setText which will trigger textChanged -> ViewModel update via slots
        self.copy_source_edit.setText(self.viewmodel.copy_source_dir)
        self.copy_json_edit.setText(self.viewmodel.copy_json_path)
        self.paste_json_edit.setText(self.viewmodel.paste_json_path)
        self.paste_output_edit.setText(self.viewmodel.paste_output_dir)
        # Update the extensions list display
        self._update_extensions_list(self.viewmodel.extensions)
        # Set initial theme
        self.theme_combo.setCurrentText(self.viewmodel.theme)
        self._apply_theme(self.viewmodel.theme)
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