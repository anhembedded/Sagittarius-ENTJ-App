"""Copy operation widget."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QLineEdit, QPushButton, QFileDialog, QMessageBox, QCheckBox
)
from PySide6.QtCore import Qt

from ...di_container import DIContainer
from ..view_models.copy_view_model import CopyViewModel
from .password_dialog import PasswordDialog


class CopyWidget(QWidget):
    """Widget for snapshot/copy operations."""
    
    def __init__(self, viewmodel: CopyViewModel, container: DIContainer):
        """
        Initialize the copy widget.
        
        Args:
            viewmodel: Copy view model.
            container: DI container for accessing settings.
        """
        super().__init__()
        self._viewmodel = viewmodel
        self._container = container
        self._extension_filter = container.get_extension_filter()
        
        self._init_ui()
        self._connect_signals()
        self._load_initial_data()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Source directory section
        source_group = QGroupBox("Source Directory")
        source_layout = QFormLayout()
        
        source_row = QHBoxLayout()
        self.source_edit = QLineEdit()
        self.source_edit.setPlaceholderText("Select directory to snapshot...")
        source_row.addWidget(self.source_edit)
        
        self.browse_source_btn = QPushButton("Browse...")
        self.browse_source_btn.clicked.connect(self._browse_source)
        source_row.addWidget(self.browse_source_btn)
        
        source_layout.addRow("Path:", source_row)
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)
        
        # Output JSON section
        json_group = QGroupBox("Output JSON File")
        json_layout = QFormLayout()
        
        json_row = QHBoxLayout()
        self.json_edit = QLineEdit()
        self.json_edit.setPlaceholderText("Select output JSON file...")
        json_row.addWidget(self.json_edit)
        
        self.browse_json_btn = QPushButton("Browse...")
        self.browse_json_btn.clicked.connect(self._browse_json)
        json_row.addWidget(self.browse_json_btn)
        
        json_layout.addRow("Path:", json_row)
        json_group.setLayout(json_layout)
        layout.addWidget(json_group)
        
        # Encryption section
        encryption_group = QGroupBox("Security Options")
        encryption_layout = QVBoxLayout()
        
        self.encrypt_checkbox = QCheckBox("🔐 Enable Encryption (Password Protected)")
        self.encrypt_checkbox.setToolTip(
            "Encrypt the snapshot file with a password.\n"
            "You will need to provide the same password when loading this snapshot."
        )
        encryption_layout.addWidget(self.encrypt_checkbox)
        
        encryption_group.setLayout(encryption_layout)
        layout.addWidget(encryption_group)
        
        # Action button
        action_layout = QHBoxLayout()
        action_layout.addStretch()
        
        self.scan_btn = QPushButton("📸 Create Snapshot")
        self.scan_btn.setObjectName("CopyButton")
        self.scan_btn.setMinimumWidth(200)
        self.scan_btn.setMinimumHeight(40)
        self.scan_btn.clicked.connect(self._on_scan_clicked)
        action_layout.addWidget(self.scan_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        layout.addStretch()
    
    def _connect_signals(self):
        """Connect signals."""
        self._viewmodel.scan_completed.connect(self._on_scan_completed)
        self._viewmodel.operation_active.connect(self._on_operation_active)
        
        # Connect text changes to viewmodel
        self.source_edit.textChanged.connect(
            lambda text: setattr(self._viewmodel, 'source_dir', text)
        )
        self.json_edit.textChanged.connect(
            lambda text: setattr(self._viewmodel, 'json_path', text)
        )
    
    def _load_initial_data(self):
        """Load initial data from view model."""
        self.source_edit.setText(self._viewmodel.source_dir)
        self.json_edit.setText(self._viewmodel.json_path)
    
    def _browse_source(self):
        """Browse for source directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Source Directory",
            self.source_edit.text()
        )
        if directory:
            self.source_edit.setText(directory)
    
    def _browse_json(self):
        """Browse for JSON output file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Snapshot As",
            self.json_edit.text(),
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.json_edit.setText(file_path)
    
    def _on_scan_clicked(self):
        """Handle scan button click."""
        source_dir = self.source_edit.text().strip()
        json_path = self.json_edit.text().strip()
        
        # Validation
        if not source_dir:
            QMessageBox.warning(self, "Invalid Input", "Please select a source directory.")
            return
        
        if not json_path:
            QMessageBox.warning(self, "Invalid Input", "Please select an output JSON file.")
            return
        
        # Get extensions
        extensions = self._extension_filter.get_extensions()
        if not extensions:
            QMessageBox.warning(
                self, 
                "No Extensions", 
                "No file extensions configured. Please add extensions in the Extensions tab."
            )
            return
        
        # Check if encryption is enabled and get password if needed
        password = None
        if self.encrypt_checkbox.isChecked():
            password = PasswordDialog.get_encryption_password(self)
            if password is None:  # User cancelled password dialog
                return
        
        # Store password for use in scan completion
        self._encryption_password = password
        
        # Start scan
        self._viewmodel.scan_directory(source_dir, extensions)
    
    def _on_scan_completed(self, snapshot):
        """Handle scan completion."""
        # Auto-save if JSON path is set
        json_path = self.json_edit.text().strip()
        if json_path:
            # Use stored encryption password from scan click
            password = getattr(self, '_encryption_password', None)
            self._viewmodel.save_snapshot(snapshot, json_path, password)
            # Clear password from memory
            self._encryption_password = None
        else:
            QMessageBox.information(
                self,
                "Scan Complete",
                f"Snapshot created with {snapshot.get_file_count()} files.\n"
                f"Please select a JSON output path to save."
            )
    
    def _on_operation_active(self, active: bool):
        """Handle operation active state."""
        self.scan_btn.setEnabled(not active)
        self.browse_source_btn.setEnabled(not active)
        self.browse_json_btn.setEnabled(not active)
        self.encrypt_checkbox.setEnabled(not active)
