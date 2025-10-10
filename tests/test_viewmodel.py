import unittest
from unittest.mock import MagicMock, patch
import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QSettings

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.viewmodel import ViewModel
from src.model import Model

class TestViewModel(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Create a QApplication instance before any tests run."""
        cls.app = QApplication.instance()
        if cls.app is None:
            # Use the "offscreen" platform plugin to avoid GUI errors in headless environments
            cls.app = QApplication(['-platform', 'offscreen'])

    def setUp(self):
        """Set up a fresh ViewModel for each test."""
        # Use test-specific settings to avoid interfering with the app's real settings
        self.settings = QSettings("TestOrg", "TestApp")
        self.settings.clear() # Ensure clean settings for each test

        self.mock_model = MagicMock(spec=Model)

        # Patch QSettings to use our test instance
        with patch('src.viewmodel.QSettings', return_value=self.settings):
            self.viewmodel = ViewModel(self.mock_model)

        # To test signals, we connect them to mock slots.
        # We can't mock the 'emit' method as it's read-only.
        self.mock_status_slot = MagicMock()
        self.viewmodel.status_update.connect(self.mock_status_slot)


    def tearDown(self):
        """Clean up settings after each test."""
        self.settings.clear()

    def test_initialization(self):
        """Test that the ViewModel initializes with default values."""
        self.assertEqual(self.viewmodel.theme, 'light')
        self.assertIn('.py', self.viewmodel.extensions)
        self.assertEqual(self.viewmodel.copy_source_dir, '')

    def test_set_theme(self):
        """Test the theme property setter."""
        mock_theme_slot = MagicMock()
        self.viewmodel.theme_changed.connect(mock_theme_slot)

        self.viewmodel.theme = 'dark'
        self.assertEqual(self.viewmodel.theme, 'dark')
        # Check that the setting was saved
        self.assertEqual(self.settings.value("theme"), 'dark')
        # Check that the signal was emitted
        mock_theme_slot.assert_called_once_with('dark')

    def test_set_theme_no_change(self):
        """Test that setting the same theme does not trigger a change."""
        mock_theme_slot = MagicMock()
        self.viewmodel.theme_changed.connect(mock_theme_slot)

        self.viewmodel.theme = 'light' # Already light by default
        # Signal should not have been emitted
        mock_theme_slot.assert_not_called()

    def test_add_extension(self):
        """Test adding a new extension."""
        mock_ext_slot = MagicMock()
        self.viewmodel.extensions_changed.connect(mock_ext_slot)

        initial_count = len(self.viewmodel.extensions)
        self.viewmodel.add_extension('.html')

        self.assertIn('.html', self.viewmodel.extensions)
        self.assertEqual(len(self.viewmodel.extensions), initial_count + 1)
        mock_ext_slot.assert_called_once()

    def test_add_existing_extension(self):
        """Test adding an extension that already exists."""
        mock_ext_slot = MagicMock()
        self.viewmodel.extensions_changed.connect(mock_ext_slot)

        initial_count = len(self.viewmodel.extensions)
        self.viewmodel.add_extension('.py') # Already exists

        self.assertEqual(len(self.viewmodel.extensions), initial_count)
        mock_ext_slot.assert_not_called()

    def test_add_invalid_extension(self):
        """Test adding an invalid extension format."""
        mock_ext_slot = MagicMock()
        self.viewmodel.extensions_changed.connect(mock_ext_slot)

        initial_count = len(self.viewmodel.extensions)
        self.viewmodel.add_extension('invalid') # Does not start with '.'

        self.assertEqual(len(self.viewmodel.extensions), initial_count)
        mock_ext_slot.assert_not_called()
        self.mock_status_slot.assert_called_with("Invalid extension format: 'invalid'. Must start with '.'", 3000)

    def test_remove_extension(self):
        """Test removing an existing extension."""
        mock_ext_slot = MagicMock()
        self.viewmodel.extensions_changed.connect(mock_ext_slot)

        initial_count = len(self.viewmodel.extensions)
        self.viewmodel.remove_extension('.py')

        self.assertNotIn('.py', self.viewmodel.extensions)
        self.assertEqual(len(self.viewmodel.extensions), initial_count - 1)
        mock_ext_slot.assert_called_once()

    def test_set_paths(self):
        """Test the setters for various path properties."""
        test_path = "/test/path/source"
        self.viewmodel.copy_source_dir = test_path
        self.assertEqual(self.viewmodel.copy_source_dir, test_path)
        self.assertEqual(self.settings.value("paths/copySourceDir"), test_path)
        self.mock_status_slot.assert_called_with("Copy source path updated.", 1500)

        test_json_path = "/test/path/file.json"
        self.viewmodel.copy_json_path = test_json_path
        self.assertEqual(self.viewmodel.copy_json_path, test_json_path)
        self.assertEqual(self.settings.value("paths/copyJsonPath"), test_json_path)
        self.mock_status_slot.assert_called_with("Copy JSON path updated.", 1500)


if __name__ == '__main__':
    unittest.main()