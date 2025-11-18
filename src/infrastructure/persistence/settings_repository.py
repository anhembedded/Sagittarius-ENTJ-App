"""Settings repository for persistent configuration."""

from typing import Any, List, Optional
from PySide6.QtCore import QSettings

from ...shared.constants import APP_NAME, APP_ORGANIZATION


class SettingsRepository:
    """Manages application settings using QSettings."""
    
    def __init__(self, app_name: str = APP_NAME, organization: str = APP_ORGANIZATION):
        """
        Initialize the settings repository.
        
        Args:
            app_name: Application name for settings.
            organization: Organization name for settings.
        """
        self._settings = QSettings(organization, app_name)
    
    def get(self, key: str, default: Any = None, value_type: type = None) -> Any:
        """
        Get a setting value.
        
        Args:
            key: Settings key.
            default: Default value if key doesn't exist.
            value_type: Expected type of the value (for type conversion).
            
        Returns:
            Setting value or default.
        """
        if value_type is not None:
            return self._settings.value(key, defaultValue=default, type=value_type)
        return self._settings.value(key, defaultValue=default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a setting value.
        
        Args:
            key: Settings key.
            value: Value to store.
        """
        self._settings.setValue(key, value)
    
    def remove(self, key: str) -> None:
        """
        Remove a setting.
        
        Args:
            key: Settings key to remove.
        """
        self._settings.remove(key)
    
    def contains(self, key: str) -> bool:
        """
        Check if a setting exists.
        
        Args:
            key: Settings key to check.
            
        Returns:
            True if setting exists, False otherwise.
        """
        return self._settings.contains(key)
    
    def clear(self) -> None:
        """Clear all settings."""
        self._settings.clear()
    
    def sync(self) -> None:
        """Force synchronization of settings to persistent storage."""
        self._settings.sync()
    
    def get_string(self, key: str, default: str = "") -> str:
        """Get a string setting."""
        return self.get(key, default, str)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """Get an integer setting."""
        return self.get(key, default, int)
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get a boolean setting."""
        return self.get(key, default, bool)
    
    def get_list(self, key: str, default: Optional[List] = None) -> List:
        """Get a list setting."""
        if default is None:
            default = []
        return self.get(key, default, list)
