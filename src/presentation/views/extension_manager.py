"""Extension manager widget."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QListWidget, QPushButton, QLineEdit, QMessageBox, QLabel
)
from PySide6.QtCore import Qt, Signal

from ...di_container import DIContainer
from ...shared.constants import SETTINGS_EXTENSIONS


class ExtensionManagerWidget(QWidget):
    """Widget for managing file extensions."""
    
    extensions_changed = Signal(list)
    
    def __init__(self, container: DIContainer):
        """
        Initialize the extension manager widget.
        
        Args:
            container: DI container.
        """
        super().__init__()
        self._container = container
        self._extension_filter = container.get_extension_filter()
        self._settings = container.get_settings_repository()
        
        self._init_ui()
        self._load_extensions()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Info label
        info_label = QLabel(
            "Configure which file extensions to include in snapshots.\n"
            "Extensions should start with a dot (e.g., .py, .txt)"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Extension list section
        list_group = QGroupBox("File Extensions")
        list_layout = QVBoxLayout()
        
        self.extension_list = QListWidget()
        self.extension_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        list_layout.addWidget(self.extension_list)
        
        list_group.setLayout(list_layout)
        layout.addWidget(list_group)
        
        # Add extension section
        add_group = QGroupBox("Add Extension")
        add_layout = QHBoxLayout()
        
        self.extension_input = QLineEdit()
        self.extension_input.setPlaceholderText("e.g., .py, .txt, .cpp")
        self.extension_input.returnPressed.connect(self._on_add_clicked)
        add_layout.addWidget(self.extension_input)
        
        self.add_btn = QPushButton("➕ Add")
        self.add_btn.clicked.connect(self._on_add_clicked)
        add_layout.addWidget(self.add_btn)
        
        add_group.setLayout(add_layout)
        layout.addWidget(add_group)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.remove_btn = QPushButton("❌ Remove Selected")
        self.remove_btn.clicked.connect(self._on_remove_clicked)
        action_layout.addWidget(self.remove_btn)
        
        action_layout.addStretch()
        
        self.reset_btn = QPushButton("🔄 Reset to Defaults")
        self.reset_btn.clicked.connect(self._on_reset_clicked)
        action_layout.addWidget(self.reset_btn)
        
        layout.addLayout(action_layout)
        
        layout.addStretch()
    
    def _load_extensions(self):
        """Load extensions into the list."""
        self.extension_list.clear()
        extensions = self._extension_filter.get_extensions()
        self.extension_list.addItems(extensions)
    
    def _save_extensions(self):
        """Save extensions to settings."""
        extensions = self._extension_filter.get_extensions()
        self._settings.set(SETTINGS_EXTENSIONS, extensions)
        self.extensions_changed.emit(extensions)
    
    def _on_add_clicked(self):
        """Handle add button click."""
        extension = self.extension_input.text().strip()
        
        if not extension:
            return
        
        # Ensure it starts with a dot
        if not extension.startswith('.'):
            extension = '.' + extension
        
        # Check if already exists
        if extension in self._extension_filter:
            QMessageBox.information(
                self,
                "Already Exists",
                f"Extension '{extension}' is already in the list."
            )
            return
        
        # Add to filter
        self._extension_filter.add_extension(extension)
        self._save_extensions()
        self._load_extensions()
        
        # Clear input
        self.extension_input.clear()
    
    def _on_remove_clicked(self):
        """Handle remove button click."""
        current_item = self.extension_list.currentItem()
        
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select an extension to remove.")
            return
        
        extension = current_item.text()
        
        # Confirm removal
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Remove extension '{extension}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self._extension_filter.remove_extension(extension)
            self._save_extensions()
            self._load_extensions()
    
    def _on_reset_clicked(self):
        """Handle reset button click."""
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Reset to default extensions (.txt, .py, .md, .cpp, .h, .hpp, .c)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            from ...shared.constants import DEFAULT_EXTENSIONS
            self._extension_filter.set_extensions(DEFAULT_EXTENSIONS)
            self._save_extensions()
            self._load_extensions()
