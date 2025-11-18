"""Unit tests for DirectorySnapshot domain model."""

import pytest
from datetime import datetime

from src.domain.models.snapshot import DirectorySnapshot
from src.domain.models.file_entry import FileEntry
from src.domain.models.directory_entry import DirectoryEntry
from src.shared.exceptions import ValidationError


def test_snapshot_creation():
    """Test creating a new snapshot."""
    snapshot = DirectorySnapshot(root_path="/test/path")
    
    assert snapshot.root_path == "/test/path"
    assert snapshot.get_file_count() == 0
    assert snapshot.get_directory_count() == 0
    assert isinstance(snapshot.created_at, datetime)


def test_snapshot_add_directory():
    """Test adding directories to snapshot."""
    snapshot = DirectorySnapshot(root_path="/test")
    
    snapshot.add_directory("src")
    snapshot.add_directory("src/domain")
    
    assert snapshot.get_directory_count() == 2
    assert all(isinstance(d, DirectoryEntry) for d in snapshot.directories)


def test_snapshot_add_file():
    """Test adding files to snapshot."""
    snapshot = DirectorySnapshot(root_path="/test")
    
    file1 = FileEntry(relative_path="test1.py", content=b"content1")
    file2 = FileEntry(relative_path="test2.py", content=b"content2")
    
    snapshot.add_file(file1)
    snapshot.add_file(file2)
    
    assert snapshot.get_file_count() == 2
    assert all(isinstance(f, FileEntry) for f in snapshot.files)


def test_snapshot_get_total_size():
    """Test calculating total size of files."""
    snapshot = DirectorySnapshot(root_path="/test")
    
    snapshot.add_file(FileEntry(relative_path="a.txt", content=b"12345"))  # 5 bytes
    snapshot.add_file(FileEntry(relative_path="b.txt", content=b"1234567890"))  # 10 bytes
    
    assert snapshot.get_total_size() == 15


def test_snapshot_validate_success():
    """Test validation of valid snapshot."""
    snapshot = DirectorySnapshot(root_path="/test")
    snapshot.add_file(FileEntry(relative_path="test.py", content=b"test"))
    
    assert snapshot.validate() is True


def test_snapshot_validate_missing_root():
    """Test validation fails without root path."""
    snapshot = DirectorySnapshot(root_path="")
    
    with pytest.raises(ValidationError, match="must have a root_path"):
        snapshot.validate()


def test_snapshot_validate_duplicate_files():
    """Test validation fails with duplicate file paths."""
    snapshot = DirectorySnapshot(root_path="/test")
    
    snapshot.add_file(FileEntry(relative_path="test.py", content=b"a"))
    snapshot.add_file(FileEntry(relative_path="test.py", content=b"b"))
    
    with pytest.raises(ValidationError, match="duplicate file paths"):
        snapshot.validate()


def test_snapshot_to_dict():
    """Test converting snapshot to dictionary."""
    snapshot = DirectorySnapshot(root_path="/test")
    snapshot.add_directory("src")
    
    file_entry = FileEntry(relative_path="test.py", content=b"hello")
    file_entry.set_encoded_content("aGVsbG8=")  # base64 of "hello"
    snapshot.add_file(file_entry)
    
    data = snapshot.to_dict()
    
    assert data['root_path'] == "/test"
    assert 'created_at' in data
    assert 'src' in data['directories']
    assert len(data['files']) == 1
    assert data['files'][0]['path'] == "test.py"


def test_snapshot_from_dict():
    """Test creating snapshot from dictionary."""
    data = {
        'root_path': "/test",
        'created_at': "2025-01-01T12:00:00",
        'directories': ['src', 'tests'],
        'metadata': {}
    }
    
    files = [
        FileEntry(relative_path="test.py", content=b"content")
    ]
    
    snapshot = DirectorySnapshot.from_dict(data, files)
    
    assert snapshot.root_path == "/test"
    assert snapshot.get_directory_count() == 2
    assert snapshot.get_file_count() == 1


def test_snapshot_statistics():
    """Test getting snapshot statistics."""
    snapshot = DirectorySnapshot(root_path="/test")
    snapshot.add_directory("src")
    snapshot.add_file(FileEntry(relative_path="test.py", content=b"12345"))
    snapshot.add_file(FileEntry(relative_path="test.txt", content=b"67890"))
    
    stats = snapshot.get_statistics()
    
    assert stats['root_path'] == "/test"
    assert stats['directory_count'] == 1
    assert stats['file_count'] == 2
    assert stats['total_size_bytes'] == 10
    assert '.py' in stats['file_extensions']
    assert '.txt' in stats['file_extensions']
