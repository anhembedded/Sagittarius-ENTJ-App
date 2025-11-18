"""Unit tests for FileEntry domain model."""

import pytest

from src.domain.models.file_entry import FileEntry
from src.shared.exceptions import ValidationError


def test_file_entry_creation():
    """Test creating a file entry."""
    entry = FileEntry(relative_path="test.py", content=b"hello world")
    
    assert entry.relative_path == "test.py"
    assert entry.content == b"hello world"
    assert entry.size == 11
    assert len(entry.checksum) == 64  # SHA-256 hex digest length


def test_file_entry_path_normalization():
    """Test path normalization."""
    entry = FileEntry(relative_path="src\\domain\\test.py", content=b"test")
    
    # Path should be normalized to forward slashes
    assert entry.relative_path == "src/domain/test.py"


def test_file_entry_checksum_validation():
    """Test checksum validation."""
    entry = FileEntry(relative_path="test.py", content=b"content")
    
    assert entry.validate_checksum() is True


def test_file_entry_checksum_mismatch():
    """Test checksum validation fails after content change."""
    entry = FileEntry(relative_path="test.py", content=b"original")
    original_checksum = entry.checksum
    
    # Manually change content (simulating corruption)
    entry.content = b"modified"
    
    # Checksum should no longer match
    assert entry.validate_checksum() is False


def test_file_entry_get_extension():
    """Test getting file extension."""
    entry1 = FileEntry(relative_path="test.py", content=b"")
    entry2 = FileEntry(relative_path="README.md", content=b"")
    entry3 = FileEntry(relative_path="noextension", content=b"")
    
    assert entry1.get_extension() == ".py"
    assert entry2.get_extension() == ".md"
    assert entry3.get_extension() == ""


def test_file_entry_encoded_content():
    """Test setting and getting encoded content."""
    entry = FileEntry(relative_path="test.txt", content=b"hello")
    
    entry.set_encoded_content("aGVsbG8=")
    
    assert entry.get_encoded_content() == "aGVsbG8="


def test_file_entry_to_dict_without_content():
    """Test converting to dict without encoded content raises error."""
    entry = FileEntry(relative_path="test.py", content=b"test")
    
    with pytest.raises(ValidationError, match="no encoded content"):
        entry.to_dict(include_content=True)


def test_file_entry_to_dict_with_content():
    """Test converting to dict with encoded content."""
    entry = FileEntry(relative_path="test.py", content=b"hello")
    entry.set_encoded_content("aGVsbG8=")
    
    data = entry.to_dict(include_content=True)
    
    assert data['path'] == "test.py"
    assert data['size'] == 5
    assert 'checksum' in data
    assert data['content_base64'] == "aGVsbG8="


def test_file_entry_to_dict_without_content_param():
    """Test converting to dict without content."""
    entry = FileEntry(relative_path="test.py", content=b"hello")
    
    data = entry.to_dict(include_content=False)
    
    assert data['path'] == "test.py"
    assert data['size'] == 5
    assert 'checksum' in data
    assert 'content_base64' not in data


def test_file_entry_from_dict():
    """Test creating file entry from dictionary."""
    data = {
        'path': "test.py",
        'size': 5,
        'checksum': "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"  # SHA-256 of "hello"
    }
    
    entry = FileEntry.from_dict(data, b"hello")
    
    assert entry.relative_path == "test.py"
    assert entry.content == b"hello"
    assert entry.size == 5


def test_file_entry_from_dict_checksum_mismatch():
    """Test creating from dict with wrong checksum raises error."""
    data = {
        'path': "test.py",
        'size': 5,
        'checksum': "wrong_checksum_value"
    }
    
    with pytest.raises(ValidationError, match="Checksum mismatch"):
        FileEntry.from_dict(data, b"hello")


def test_file_entry_str_repr():
    """Test string representations."""
    entry = FileEntry(relative_path="test.py", content=b"12345")
    
    str_repr = str(entry)
    assert "test.py" in str_repr
    assert "5 bytes" in str_repr
    
    repr_str = repr(entry)
    assert "FileEntry" in repr_str
    assert "test.py" in repr_str
