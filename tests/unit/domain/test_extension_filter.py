"""Unit tests for ExtensionFilter service."""

import pytest

from src.domain.services.extension_filter import ExtensionFilter


def test_extension_filter_initialization():
    """Test creating extension filter with default extensions."""
    filter = ExtensionFilter()
    
    assert len(filter) > 0
    assert '.py' in filter


def test_extension_filter_custom_extensions():
    """Test creating with custom extensions."""
    filter = ExtensionFilter(['.txt', '.md'])
    
    assert len(filter) == 2
    assert '.txt' in filter
    assert '.md' in filter


def test_extension_filter_add_extension():
    """Test adding an extension."""
    filter = ExtensionFilter([])
    
    filter.add_extension('.py')
    
    assert '.py' in filter
    assert len(filter) == 1


def test_extension_filter_add_without_dot():
    """Test adding extension without leading dot."""
    filter = ExtensionFilter([])
    
    filter.add_extension('py')  # Without dot
    
    assert '.py' in filter


def test_extension_filter_case_insensitive():
    """Test that extensions are case-insensitive."""
    filter = ExtensionFilter([])
    
    filter.add_extension('.PY')
    
    assert '.py' in filter
    assert '.PY' in filter


def test_extension_filter_remove_extension():
    """Test removing an extension."""
    filter = ExtensionFilter(['.py', '.txt'])
    
    filter.remove_extension('.py')
    
    assert '.py' not in filter
    assert '.txt' in filter


def test_extension_filter_is_allowed():
    """Test checking if filename is allowed."""
    filter = ExtensionFilter(['.py', '.txt'])
    
    assert filter.is_allowed('test.py') is True
    assert filter.is_allowed('README.txt') is True
    assert filter.is_allowed('image.jpg') is False
    assert filter.is_allowed('noextension') is False


def test_extension_filter_is_allowed_case_insensitive():
    """Test that file checking is case-insensitive."""
    filter = ExtensionFilter(['.py'])
    
    assert filter.is_allowed('test.PY') is True
    assert filter.is_allowed('TEST.Py') is True


def test_extension_filter_get_extensions():
    """Test getting list of extensions."""
    filter = ExtensionFilter(['.py', '.txt', '.md'])
    
    extensions = filter.get_extensions()
    
    assert isinstance(extensions, list)
    assert len(extensions) == 3
    assert extensions == sorted(extensions)  # Should be sorted


def test_extension_filter_set_extensions():
    """Test replacing all extensions."""
    filter = ExtensionFilter(['.py', '.txt'])
    
    filter.set_extensions(['.cpp', '.h'])
    
    assert '.py' not in filter
    assert '.txt' not in filter
    assert '.cpp' in filter
    assert '.h' in filter


def test_extension_filter_clear():
    """Test clearing all extensions."""
    filter = ExtensionFilter(['.py', '.txt'])
    
    filter.clear()
    
    assert len(filter) == 0


def test_extension_filter_len():
    """Test length of filter."""
    filter = ExtensionFilter(['.py', '.txt', '.md'])
    
    assert len(filter) == 3


def test_extension_filter_contains():
    """Test 'in' operator."""
    filter = ExtensionFilter(['.py', '.txt'])
    
    assert '.py' in filter
    assert 'py' in filter  # Should work without dot too
    assert '.cpp' not in filter


def test_extension_filter_str_repr():
    """Test string representations."""
    filter = ExtensionFilter(['.py', '.txt'])
    
    str_repr = str(filter)
    assert '.py' in str_repr
    assert '.txt' in str_repr
    
    repr_str = repr(filter)
    assert 'ExtensionFilter' in repr_str
