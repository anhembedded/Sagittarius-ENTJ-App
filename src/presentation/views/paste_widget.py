"""Paste operation widget."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QTextEdit
)
from PySide6.QtCore import Qt

from ..view_models.paste_view_model import PasteViewModel
from .password_dialog import PasswordDialog
from ...shared.exceptions import DecryptionError, InvalidPasswordError


class PasteWidget(QWidget):
    """Widget for restore/paste operations."""
    
    def __init__(self, viewmodel: PasteViewModel):
        """
        Initialize the paste widget.
        
        Args:
            viewmodel: Paste view model.
        """
        super().__init__()
        self._viewmodel = viewmodel
        
        self._init_ui()
        self._connect_signals()
        self._load_initial_data()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Input JSON section
        json_group = QGroupBox("Input JSON File")
        json_layout = QFormLayout()
        
        json_row = QHBoxLayout()
        self.json_edit = QLineEdit()
        self.json_edit.setPlaceholderText("Select snapshot JSON file...")
        json_row.addWidget(self.json_edit)
        
        self.browse_json_btn = QPushButton("Browse...")
        self.browse_json_btn.clicked.connect(self._browse_json)
        json_row.addWidget(self.browse_json_btn)
        
        json_layout.addRow("Path:", json_row)
        
        load_row = QHBoxLayout()
        load_row.addStretch()
        self.load_btn = QPushButton("📂 Load Snapshot")
        self.load_btn.setMinimumWidth(150)
        self.load_btn.clicked.connect(self._on_load_clicked)
        load_row.addWidget(self.load_btn)
        load_row.addStretch()
        
        json_layout.addRow("", load_row)
        json_group.setLayout(json_layout)
        layout.addWidget(json_group)
        
        # Snapshot info section
        info_group = QGroupBox("Snapshot Information")
        info_layout = QVBoxLayout()
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(100)
        self.info_text.setPlaceholderText("Load a snapshot to see details...")
        info_layout.addWidget(self.info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Output directory section
        output_group = QGroupBox("Output Directory")
        output_layout = QFormLayout()
        
        output_row = QHBoxLayout()
        self.output_edit = QLineEdit()
        self.output_edit.setPlaceholderText("Select directory to recreate into...")
        output_row.addWidget(self.output_edit)
        
        self.browse_output_btn = QPushButton("Browse...")
        self.browse_output_btn.clicked.connect(self._browse_output)
        output_row.addWidget(self.browse_output_btn)
        
        output_layout.addRow("Path:", output_row)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Action button
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        
        self.recreate_btn = QPushButton("📂 Restore Directory")
        self.recreate_btn.setObjectName("PasteButton")
        self.recreate_btn.setMinimumWidth(200)
        self.recreate_btn.setMinimumHeight(40)
        self.recreate_btn.setEnabled(False)
        self.recreate_btn.clicked.connect(self._on_recreate_clicked)
        action_layout.addWidget(self.recreate_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        layout.addStretch()
    
    def _connect_signals(self):
        """Connect signals."""
        self._viewmodel.load_completed.connect(self._on_load_completed)
        self._viewmodel.load_error.connect(self._on_load_error)
        self._viewmodel.operation_active.connect(self._on_operation_active)
        
        # Connect text changes to viewmodel
        self.json_edit.textChanged.connect(
            lambda text: setattr(self._viewmodel, 'json_path', text)
        )
        self.output_edit.textChanged.connect(
            lambda text: setattr(self._viewmodel, 'output_dir', text)
        )
    
    def _load_initial_data(self):
        """Load initial data from view model."""
        self.json_edit.setText(self._viewmodel.json_path)
        self.output_edit.setText(self._viewmodel.output_dir)
    
    def _browse_json(self):
        """Browse for JSON input file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Snapshot File",
            self.json_edit.text(),
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.json_edit.setText(file_path)
    
    def _browse_output(self):
        """Browse for output directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            self.output_edit.text()
        )
        if directory:
            self.output_edit.setText(directory)
    
    def _on_load_clicked(self):
        """Handle load button click."""
        json_path = self.json_edit.text().strip()
        
        if not json_path:
            QMessageBox.warning(self, "Invalid Input", "Please select a JSON file to load.")
            return
        
        # Start load operation
        self._viewmodel.load_snapshot(json_path)
    
    def _on_load_error(self, error_msg: str, exception) -> None:
        """
        Handle load errors from ViewModel.
        
        Args:
            error_msg: Error message string.
            exception: The exception object that was raised.
        """
        # Check if this is a DecryptionError (file is encrypted)
        if exception and isinstance(exception, DecryptionError):
            # Ask user for password
            password = PasswordDialog.get_decryption_password(self)
            if password is not None:
                # Retry with password
                json_path = self.json_edit.text().strip()
                self._viewmodel.load_snapshot(json_path, password)
            # else: User cancelled, do nothing
        elif exception and isinstance(exception, InvalidPasswordError):
            # Wrong password - show error and ask again
            QMessageBox.critical(
                self,
                "Decryption Failed",
                "The password you entered is incorrect.\n"
                "Please try again."
            )
            password = PasswordDialog.get_decryption_password(self)
            if password is not None:
                json_path = self.json_edit.text().strip()
                self._viewmodel.load_snapshot(json_path, password)
        else:
            # Other errors - show error message
            QMessageBox.critical(
                self,
                "Load Failed",
                f"Failed to load snapshot:\n{error_msg}"
            )
    
    def _on_load_completed(self, snapshot):
        """Handle load completion."""
        # Display snapshot info
        stats = snapshot.get_statistics()
        info_text = f"""
Root Path: {stats['root_path']}
Created: {stats['created_at']}
Directories: {stats['directory_count']}
Files: {stats['file_count']}
Total Size: {stats['total_size_bytes']:,} bytes
        """.strip()
        
        self.info_text.setPlainText(info_text)
        self.recreate_btn.setEnabled(True)
    
    def _on_recreate_clicked(self):
        """Handle recreate button click."""
        output_dir = self.output_edit.text().strip()
        
        if not output_dir:
            QMessageBox.warning(self, "Invalid Input", "Please select an output directory.")
            return
        
        if not self._viewmodel.current_snapshot:
            QMessageBox.warning(self, "No Snapshot", "Please load a snapshot first.")
            return
        
        # Confirm overwrite
        reply = QMessageBox.question(
            self,
            "Confirm Recreation",
            f"This will recreate {self._viewmodel.current_snapshot.get_file_count()} files "
            f"in:\n{output_dir}\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._viewmodel.recreate_directory(
                self._viewmodel.current_snapshot,
                output_dir
            )
    
    def _on_operation_active(self, active: bool):
        """Handle operation active state."""
        self.load_btn.setEnabled(not active)
        self.recreate_btn.setEnabled(not active and self._viewmodel.current_snapshot is not None)
        self.browse_json_btn.setEnabled(not active)
        self.browse_output_btn.setEnabled(not active)
