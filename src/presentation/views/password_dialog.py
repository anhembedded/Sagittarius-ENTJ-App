"""Password input dialog for encryption/decryption."""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt


class PasswordDialog(QDialog):
    """Dialog for password input with confirmation option."""
    
    def __init__(self, title: str = "Enter Password", 
                 confirm: bool = False, 
                 parent=None):
        """
        Initialize password dialog.
        
        Args:
            title: Dialog window title.
            confirm: If True, show password confirmation field.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self._confirm = confirm
        self._password = ""
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Instructions
        if self._confirm:
            instruction_text = (
                "Create a strong password to encrypt your snapshot.\n"
                "⚠️ Important: You cannot recover the data if you forget this password!"
            )
        else:
            instruction_text = "Enter the password to decrypt this snapshot:"
        
        instruction_label = QLabel(instruction_text)
        instruction_label.setWordWrap(True)
        layout.addWidget(instruction_label)
        
        # Password input
        password_label = QLabel("Password:")
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter password...")
        self.password_input.returnPressed.connect(self._on_ok)
        layout.addWidget(self.password_input)
        
        # Confirm password (for encryption only)
        if self._confirm:
            confirm_label = QLabel("Confirm Password:")
            layout.addWidget(confirm_label)
            
            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.confirm_input.setPlaceholderText("Re-enter password...")
            self.confirm_input.returnPressed.connect(self._on_ok)
            layout.addWidget(self.confirm_input)
        
        # Show password checkbox
        self.show_password_cb = QCheckBox("Show password")
        self.show_password_cb.toggled.connect(self._toggle_password_visibility)
        layout.addWidget(self.show_password_cb)
        
        # Password strength indicator (for encryption only)
        if self._confirm:
            self.strength_label = QLabel()
            self.strength_label.setStyleSheet("color: #666;")
            layout.addWidget(self.strength_label)
            self.password_input.textChanged.connect(self._update_strength)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self._on_ok)
        ok_btn.setDefault(True)
        ok_btn.setMinimumWidth(100)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMinimumWidth(100)
        
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Focus on password input
        self.password_input.setFocus()
    
    def _toggle_password_visibility(self, checked: bool):
        """Toggle password visibility."""
        mode = QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        self.password_input.setEchoMode(mode)
        if self._confirm:
            self.confirm_input.setEchoMode(mode)
    
    def _update_strength(self, password: str):
        """Update password strength indicator."""
        if not self._confirm:
            return
        
        length = len(password)
        
        if length == 0:
            self.strength_label.setText("")
            return
        
        # Check password strength
        has_lower = any(c.islower() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        score = sum([has_lower, has_upper, has_digit, has_special])
        
        if length < 8:
            strength = "❌ Too short (minimum 8 characters)"
            color = "#d32f2f"
        elif length < 12 and score < 3:
            strength = "⚠️ Weak (add mixed case, numbers, symbols)"
            color = "#f57c00"
        elif length < 16 and score < 4:
            strength = "✓ Medium (consider making it longer)"
            color = "#fbc02d"
        else:
            strength = "✅ Strong"
            color = "#388e3c"
        
        self.strength_label.setText(f"Strength: {strength}")
        self.strength_label.setStyleSheet(f"color: {color}; font-weight: bold;")
    
    def _on_ok(self):
        """Handle OK button click."""
        password = self.password_input.text()
        
        # Validate password
        if not password:
            QMessageBox.warning(
                self, 
                "Error", 
                "Password cannot be empty."
            )
            self.password_input.setFocus()
            return
        
        # Check minimum length for encryption
        if self._confirm and len(password) < 8:
            QMessageBox.warning(
                self,
                "Weak Password",
                "Password must be at least 8 characters long for security.\n"
                "Please use a stronger password."
            )
            self.password_input.setFocus()
            return
        
        # Confirm password match (for encryption)
        if self._confirm:
            confirm = self.confirm_input.text()
            if password != confirm:
                QMessageBox.warning(
                    self,
                    "Error",
                    "Passwords do not match. Please try again."
                )
                self.confirm_input.clear()
                self.confirm_input.setFocus()
                return
        
        self._password = password
        self.accept()
    
    def get_password(self) -> str:
        """
        Get the entered password.
        
        Returns:
            The password entered by user.
        """
        return self._password
    
    @staticmethod
    def get_encryption_password(parent=None) -> str:
        """
        Show dialog to get password for encryption.
        
        Args:
            parent: Parent widget.
            
        Returns:
            Password string, or empty string if cancelled.
        """
        dialog = PasswordDialog(
            title="Encrypt Snapshot",
            confirm=True,
            parent=parent
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_password()
        return ""
    
    @staticmethod
    def get_decryption_password(parent=None) -> str:
        """
        Show dialog to get password for decryption.
        
        Args:
            parent: Parent widget.
            
        Returns:
            Password string, or empty string if cancelled.
        """
        dialog = PasswordDialog(
            title="Decrypt Snapshot",
            confirm=False,
            parent=parent
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.get_password()
        return ""
