"""Integration tests for the complete snapshot workflow."""

import os
import json
import tempfile
import shutil
from pathlib import Path

import pytest

from src.di_container import DIContainer
from src.application.dto.scan_request import ScanRequest
from src.application.dto.recreate_request import RecreateRequest


@pytest.fixture
def temp_dirs():
    """Create temporary directories for testing."""
    source_dir = tempfile.mkdtemp(prefix="sagittarius_source_")
    output_dir = tempfile.mkdtemp(prefix="sagittarius_output_")
    json_file = os.path.join(tempfile.gettempdir(), "test_snapshot.json")
    
    yield source_dir, output_dir, json_file
    
    # Cleanup
    shutil.rmtree(source_dir, ignore_errors=True)
    shutil.rmtree(output_dir, ignore_errors=True)
    if os.path.exists(json_file):
        os.remove(json_file)


@pytest.fixture
def sample_files(temp_dirs):
    """Create sample files in source directory."""
    source_dir, _, _ = temp_dirs
    
    # Create directory structure
    os.makedirs(os.path.join(source_dir, "subfolder1"))
    os.makedirs(os.path.join(source_dir, "subfolder2", "nested"))
    
    # Create sample files
    files = {
        "readme.txt": "This is a readme file\nWith multiple lines\n",
        "config.json": '{"key": "value", "number": 42}',
        "subfolder1/file1.py": "def hello():\n    print('Hello World')\n",
        "subfolder1/file2.txt": "Another text file\n",
        "subfolder2/data.md": "# Markdown\n\nSome content\n",
        "subfolder2/nested/deep.log": "Log entry 1\nLog entry 2\n",
    }
    
    for rel_path, content in files.items():
        file_path = os.path.join(source_dir, rel_path)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    return files


class TestFullWorkflow:
    """Test the complete snapshot workflow: scan -> save -> load -> recreate."""
    
    def test_complete_workflow(self, temp_dirs, sample_files):
        """Test the complete workflow from scanning to recreation."""
        source_dir, output_dir, json_file = temp_dirs
        
        # Step 1: Create container and use cases
        container = DIContainer()
        scan_use_case = container.get_scan_directory_use_case()
        save_use_case = container.get_save_snapshot_use_case()
        load_use_case = container.get_load_snapshot_use_case()
        recreate_use_case = container.get_recreate_directory_use_case()
        
        # Step 2: Scan directory
        extensions = [".txt", ".py", ".json", ".md", ".log"]
        scan_request = ScanRequest(
            root_path=source_dir,
            extensions=extensions,
            progress_callback=None
        )
        
        snapshot = scan_use_case.execute(scan_request)
        
        # Verify snapshot has correct structure
        # Normalize paths for comparison
        expected_path = source_dir.replace("\\", "/")
        actual_path = snapshot.root_path.replace("\\", "/")
        assert actual_path == expected_path
        assert len(snapshot.files) == 6  # All files we created
        assert len(snapshot.directories) >= 3  # Main + 2 subfolders (+ nested)
        
        # Step 3: Save snapshot to JSON
        save_use_case.execute(snapshot, json_file)
        
        # Verify JSON file exists
        assert os.path.exists(json_file)
        assert os.path.getsize(json_file) > 0
        
        # Step 4: Load snapshot from JSON
        loaded_snapshot = load_use_case.execute(json_file)
        
        # Verify loaded snapshot matches original
        assert loaded_snapshot.root_path == snapshot.root_path
        assert len(loaded_snapshot.files) == len(snapshot.files)
        assert len(loaded_snapshot.directories) == len(snapshot.directories)
        
        # Step 5: Recreate directory
        recreate_request = RecreateRequest(
            snapshot=loaded_snapshot,
            output_path=output_dir,
            progress_callback=None
        )
        
        recreate_use_case.execute(recreate_request)
        
        # Step 6: Verify all files were recreated correctly
        for rel_path, original_content in sample_files.items():
            recreated_path = os.path.join(output_dir, rel_path)
            assert os.path.exists(recreated_path), f"File not recreated: {rel_path}"
            
            with open(recreated_path, "r", encoding="utf-8") as f:
                recreated_content = f.read()
            
            assert recreated_content == original_content, \
                f"Content mismatch for {rel_path}"
    
    def test_scan_with_extension_filter(self, temp_dirs, sample_files):
        """Test scanning with extension filtering."""
        source_dir, _, _ = temp_dirs
        
        container = DIContainer()
        scan_use_case = container.get_scan_directory_use_case()
        
        # Only scan .txt files
        scan_request = ScanRequest(
            root_path=source_dir,
            extensions=[".txt"],
            progress_callback=None
        )
        
        snapshot = scan_use_case.execute(scan_request)
        
        # Should only have .txt files
        assert len(snapshot.files) == 2  # readme.txt and subfolder1/file2.txt
        for file_entry in snapshot.files:
            assert file_entry.relative_path.endswith(".txt")
    
    def test_empty_directory_handling(self, temp_dirs):
        """Test handling of empty directories."""
        source_dir, output_dir, json_file = temp_dirs
        
        # Create only empty subdirectories
        os.makedirs(os.path.join(source_dir, "empty1"))
        os.makedirs(os.path.join(source_dir, "empty2", "nested_empty"))
        
        container = DIContainer()
        scan_use_case = container.get_scan_directory_use_case()
        save_use_case = container.get_save_snapshot_use_case()
        load_use_case = container.get_load_snapshot_use_case()
        recreate_use_case = container.get_recreate_directory_use_case()
        
        # Scan
        scan_request = ScanRequest(
            root_path=source_dir,
            extensions=[".txt"],
            progress_callback=None
        )
        snapshot = scan_use_case.execute(scan_request)
        
        # Save and load
        save_use_case.execute(snapshot, json_file)
        loaded_snapshot = load_use_case.execute(json_file)
        
        # Recreate
        recreate_request = RecreateRequest(
            snapshot=loaded_snapshot,
            output_path=output_dir,
            progress_callback=None
        )
        recreate_use_case.execute(recreate_request)
        
        # Verify no files were created (only directories)
        assert len(snapshot.files) == 0  # No .txt files in empty directories
        # Note: Empty directories are not captured in scan (by design)
        # Only directories containing files are tracked
        
        # Save and load should still work with empty snapshot
        assert os.path.exists(output_dir)
    
    def test_json_format_validation(self, temp_dirs, sample_files):
        """Test that saved JSON has correct format."""
        source_dir, _, json_file = temp_dirs
        
        container = DIContainer()
        scan_use_case = container.get_scan_directory_use_case()
        save_use_case = container.get_save_snapshot_use_case()
        
        # Scan and save
        scan_request = ScanRequest(
            root_path=source_dir,
            extensions=[".txt", ".py"],
            progress_callback=None
        )
        snapshot = scan_use_case.execute(scan_request)
        save_use_case.execute(snapshot, json_file)
        
        # Read and validate JSON structure
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Check required fields
        assert "root_path" in data
        assert "created_at" in data
        assert "directories" in data
        assert "files" in data
        assert "metadata" in data
        
        # Check files have required fields
        for file_data in data["files"]:
            assert "path" in file_data
            assert "size" in file_data
            assert "checksum" in file_data
            assert "content_base64" in file_data
    
    def test_progress_callback(self, temp_dirs, sample_files):
        """Test that progress callbacks are invoked."""
        source_dir, output_dir, json_file = temp_dirs
        
        container = DIContainer()
        scan_use_case = container.get_scan_directory_use_case()
        save_use_case = container.get_save_snapshot_use_case()
        load_use_case = container.get_load_snapshot_use_case()
        recreate_use_case = container.get_recreate_directory_use_case()
        
        # Track progress
        scan_progress = []
        recreate_progress = []
        
        def scan_callback(current: int, total: int):
            scan_progress.append((current, total))
        
        def recreate_callback(current: int, total: int):
            recreate_progress.append((current, total))
        
        # Scan with callback
        scan_request = ScanRequest(
            root_path=source_dir,
            extensions=[".txt", ".py"],
            progress_callback=scan_callback
        )
        snapshot = scan_use_case.execute(scan_request)
        
        # Save and load
        save_use_case.execute(snapshot, json_file)
        loaded_snapshot = load_use_case.execute(json_file)
        
        # Recreate with callback
        recreate_request = RecreateRequest(
            snapshot=loaded_snapshot,
            output_path=output_dir,
            progress_callback=recreate_callback
        )
        recreate_use_case.execute(recreate_request)
        
        # Verify callbacks were invoked
        assert len(scan_progress) > 0, "Scan progress callback not invoked"
        assert len(recreate_progress) > 0, "Recreate progress callback not invoked"
        
        # Verify progress values
        for current, total in scan_progress:
            assert current >= 0
            assert total >= current
