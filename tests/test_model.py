import unittest
import os
import shutil
import tempfile
import json
import sys

# Add the src directory to the Python path to allow importing the model
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.model import Model

class TestModel(unittest.TestCase):

    def setUp(self):
        """Set up a temporary directory structure for testing."""
        self.test_dir = tempfile.mkdtemp()
        self.source_dir = os.path.join(self.test_dir, "source")
        self.output_dir = os.path.join(self.test_dir, "output")
        self.json_path = os.path.join(self.test_dir, "db.json")
        os.makedirs(self.source_dir)
        os.makedirs(self.output_dir)

        # Create a sample directory structure and files
        self.dir1 = os.path.join(self.source_dir, "dir1")
        os.makedirs(self.dir1)

        self.file1_path = os.path.join(self.source_dir, "file1.txt")
        with open(self.file1_path, "w") as f:
            f.write("This is file1.")

        self.file2_path = os.path.join(self.dir1, "file2.py")
        with open(self.file2_path, "w") as f:
            f.write("print('Hello')")

        # This file should be ignored by the scanner
        self.file3_path = os.path.join(self.dir1, "file3.log")
        with open(self.file3_path, "w") as f:
            f.write("some log data")

        self.model = Model()

    def tearDown(self):
        """Clean up the temporary directory after tests."""
        shutil.rmtree(self.test_dir)

    def test_scan_directory(self):
        """Test the directory scanning functionality."""
        extensions = ['.txt', '.py']
        self.model.scan_directory(self.source_dir, extensions)

        # Check directories (should contain 'dir1')
        self.assertEqual(len(self.model.database['directories']), 1)
        self.assertIn('dir1', self.model.database['directories'])

        # Check files (should contain file1.txt and dir1/file2.py)
        self.assertEqual(len(self.model.database['files']), 2)
        paths = [f['path'] for f in self.model.database['files']]
        self.assertIn('file1.txt', paths)
        self.assertIn('dir1/file2.py', paths)
        self.assertNotIn('dir1/file3.log', paths)

        # Check content encoding
        file1_info = next(f for f in self.model.database['files'] if f['path'] == 'file1.txt')
        import base64
        decoded_content = base64.b64decode(file1_info['content_base64']).decode('utf-8')
        self.assertEqual(decoded_content, "This is file1.")

    def test_save_and_load_database(self):
        """Test saving the database to JSON and loading it back."""
        extensions = ['.txt', '.py']
        self.model.scan_directory(self.source_dir, extensions)
        original_db = self.model.database.copy()

        # Save the database
        self.model.save_database(self.json_path)
        self.assertTrue(os.path.exists(self.json_path))

        # Create a new model and load the database
        new_model = Model()
        new_model.load_database(self.json_path)

        # The loaded database should be identical to the original
        self.assertEqual(original_db, new_model.database)

    def test_recreate_from_database(self):
        """Test recreating the directory structure and files from the database."""
        extensions = ['.txt', '.py']
        self.model.scan_directory(self.source_dir, extensions)

        # Recreate in the output directory
        self.model.recreate_from_database(self.output_dir)

        # Check if directories and files were created correctly
        recreated_dir1 = os.path.join(self.output_dir, "dir1")
        self.assertTrue(os.path.isdir(recreated_dir1))

        recreated_file1 = os.path.join(self.output_dir, "file1.txt")
        self.assertTrue(os.path.isfile(recreated_file1))
        with open(recreated_file1, "r") as f:
            self.assertEqual(f.read(), "This is file1.")

        recreated_file2 = os.path.join(recreated_dir1, "file2.py")
        self.assertTrue(os.path.isfile(recreated_file2))
        with open(recreated_file2, "r") as f:
            self.assertEqual(f.read(), "print('Hello')")

        # Check that the ignored file was not created
        ignored_file = os.path.join(recreated_dir1, "file3.log")
        self.assertFalse(os.path.exists(ignored_file))

if __name__ == '__main__':
    unittest.main()