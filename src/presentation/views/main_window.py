"""Main application window."""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QTextEdit, QProgressBar, QLabel, QStatusBar, QGroupBox
)
from PySide6.QtCore import Qt

from ...di_container import DIContainer
from ..view_models.copy_view_model import CopyViewModel
from ..view_models.paste_view_model import PasteViewModel
from .copy_widget import CopyWidget
from .paste_widget import PasteWidget
from .extension_manager import ExtensionManagerWidget


class MainWindow(QWidget):
    """Main application window."""
    
    def __init__(self, container: DIContainer):
        """
        Initialize the main window.
        
        Args:
            container: Dependency injection container.
        """
        super().__init__()
        self._container = container
        
        # Create view models
        self._copy_viewmodel = CopyViewModel(container)
        self._paste_viewmodel = PasteViewModel(container)
        
        self._init_ui()
        self._connect_signals()
        self._apply_styles()
        
        # Set window properties
        self.setWindowTitle("✨ Sagittarius ENTJ - Directory Snapshot Manager ✨")
        self.setMinimumSize(900, 750)
    
    def _init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Create Copy tab
        self.copy_widget = CopyWidget(self._copy_viewmodel, self._container)
        self.tabs.addTab(self.copy_widget, "📸 Snapshot (Copy)")
        
        # Create Paste tab
        self.paste_widget = PasteWidget(self._paste_viewmodel)
        self.tabs.addTab(self.paste_widget, "📂 Restore (Paste)")
        
        # Create Extension Manager tab
        self.extension_widget = ExtensionManagerWidget(self._container)
        self.tabs.addTab(self.extension_widget, "⚙️ Extensions")
        
        main_layout.addWidget(self.tabs)
        
        # Progress section
        progress_group = QGroupBox("Progress")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)
        
        # Log section
        log_group = QGroupBox("Activity Log")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)
        
        # Status bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        main_layout.addLayout(status_layout)
    
    def _connect_signals(self):
        """Connect view model signals to UI updates."""
        # Copy view model signals
        self._copy_viewmodel.message_logged.connect(self._on_log_message)
        self._copy_viewmodel.status_update.connect(self._on_status_update)
        self._copy_viewmodel.progress_changed.connect(self._on_progress_changed)
        self._copy_viewmodel.progress_max_changed.connect(self._on_progress_max_changed)
        self._copy_viewmodel.operation_active.connect(self._on_operation_active)
        
        # Paste view model signals
        self._paste_viewmodel.message_logged.connect(self._on_log_message)
        self._paste_viewmodel.status_update.connect(self._on_status_update)
        self._paste_viewmodel.progress_changed.connect(self._on_progress_changed)
        self._paste_viewmodel.progress_max_changed.connect(self._on_progress_max_changed)
        self._paste_viewmodel.operation_active.connect(self._on_operation_active)
    
    def _apply_styles(self):
        """Apply light theme styles to the window."""
        self.setStyleSheet("""
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 10pt;
                background-color: #ffffff;
                color: #333333;
            }
            QMainWindow {
                background-color: #f5f5f5;
            }
            QGroupBox {
                border: 2px solid #d0d0d0;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
                font-weight: bold;
                background-color: #ffffff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 10px;
                background-color: #0078d4;
                color: white;
                border-radius: 4px;
                margin-left: 10px;
            }
            QProgressBar {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                text-align: center;
                height: 25px;
                background-color: #f0f0f0;
                color: #333333;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
            QTextEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 5px;
                background-color: #ffffff;
                color: #333333;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
            }
            QLineEdit {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #c0c0c0;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006cbd;
            }
            QPushButton:disabled {
                background-color: #e0e0e0;
                color: #999999;
            }
            QTabWidget::pane {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #f0f0f0;
                color: #333333;
                border: 1px solid #d0d0d0;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #0078d4;
                border-bottom: 2px solid #0078d4;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background-color: #e8e8e8;
            }
            QLabel {
                color: #333333;
                background-color: transparent;
            }
        """)
    
    def _on_log_message(self, message: str):
        """Handle log messages."""
        self.log_text.append(message)
        # Auto-scroll to bottom
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def _on_status_update(self, message: str, timeout_ms: int):
        """Handle status bar updates."""
        self.status_label.setText(message)
        # Could use QTimer to clear message after timeout if needed
    
    def _on_progress_changed(self, value: int):
        """Handle progress value changes."""
        self.progress_bar.setValue(value)
    
    def _on_progress_max_changed(self, maximum: int):
        """Handle progress maximum changes."""
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setValue(0)
    
    def _on_operation_active(self, active: bool):
        """Handle operation active state changes."""
        self.progress_bar.setVisible(active)
        if not active:
            self.progress_bar.setValue(0)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Cleanup if needed
        event.accept()
