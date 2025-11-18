# Migration Guide - Sagittarius ENTJ Refactoring

## 🎯 Overview

This document guides you through completing the refactoring from the monolithic `Sagittarius-ENTJ.py` to the new Clean Architecture structure.

## ✅ What's Been Completed

### 1. Project Structure ✓
- Created layered directory structure
- All `__init__.py` files in place
- Proper package organization

### 2. Domain Layer ✓
**Models** (`src/domain/models/`):
- ✅ `snapshot.py` - DirectorySnapshot aggregate root
- ✅ `file_entry.py` - FileEntry with checksum validation
- ✅ `directory_entry.py` - DirectoryEntry

**Services** (`src/domain/services/`):
- ✅ `extension_filter.py` - File extension filtering logic

**Interfaces** (`src/domain/interfaces/`):
- ✅ `encoder.py` - IContentEncoder interface
- ✅ `repository.py` - ISnapshotRepository interface
- ✅ `file_system.py` - IFileSystemService interface

### 3. Infrastructure Layer ✓
**Encoding** (`src/infrastructure/encoding/`):
- ✅ `base64_encoder.py` - Base64 encoder implementation

**File System** (`src/infrastructure/file_system/`):
- ✅ `file_system_service.py` - OS file operations

**Persistence** (`src/infrastructure/persistence/`):
- ✅ `json_repository.py` - JSON snapshot storage
- ✅ `settings_repository.py` - QSettings wrapper

**Logging** (`src/infrastructure/logging/`):
- ✅ `app_logger.py` - Logging configuration

### 4. Application Layer ✓
**Use Cases** (`src/application/use_cases/`):
- ✅ `scan_directory.py` - Scan and create snapshot
- ✅ `save_snapshot.py` - Save snapshot to JSON
- ✅ `load_snapshot.py` - Load snapshot from JSON
- ✅ `recreate_directory.py` - Recreate directory from snapshot

**DTOs** (`src/application/dto/`):
- ✅ `scan_request.py` - Scan parameters
- ✅ `recreate_request.py` - Recreate parameters

### 5. Shared Layer ✓
- ✅ `exceptions.py` - Custom exception hierarchy
- ✅ `constants.py` - Application constants
- ✅ `utils.py` - Helper functions

### 6. Dependency Injection ✓
- ✅ `di_container.py` - DI container for all dependencies

## 🔄 What Needs to Be Done

### Priority 1: Presentation Layer (Critical)
You need to extract UI code from `Sagittarius-ENTJ.py` and refactor into:

#### `src/presentation/workers/`
1. **`worker_signals.py`** - Extract from old `WorkerSignals` class:
   ```python
   # Signals for async operations
   class WorkerSignals(QObject):
       error = Signal(str)
       finished = Signal()
       log_message = Signal(str)
       progress_update = Signal(int)
       progress_max = Signal(int)
   ```

2. **`async_worker.py`** - Generic QRunnable worker:
   ```python
   class AsyncWorker(QRunnable):
       def __init__(self, fn, *args, **kwargs):
           # Execute function in background thread
   ```

#### `src/presentation/view_models/`
3. **`copy_view_model.py`** - Manages Copy tab state:
   ```python
   class CopyViewModel(QObject):
       def __init__(self, container: DIContainer):
           self._scan_use_case = container.get_scan_directory_use_case()
           self._save_use_case = container.get_save_snapshot_use_case()
       
       def scan_directory(self, path: str, extensions: List[str]):
           # Execute scan use case asynchronously
       
       def save_snapshot(self, snapshot, path: str):
           # Execute save use case
   ```

4. **`paste_view_model.py`** - Manages Paste tab state:
   ```python
   class PasteViewModel(QObject):
       def __init__(self, container: DIContainer):
           self._load_use_case = container.get_load_snapshot_use_case()
           self._recreate_use_case = container.get_recreate_directory_use_case()
       
       def load_snapshot(self, path: str):
           # Execute load use case
       
       def recreate_directory(self, snapshot, output_path: str):
           # Execute recreate use case asynchronously
   ```

#### `src/presentation/views/`
5. **`main_window.py`** - Extract main window UI:
   - Extract from old code (lines ~400-500)
   - Use view models for logic
   - Connect signals/slots

6. **`copy_widget.py`** - Extract Copy tab:
   - Extract from old code (lines ~500-700)
   - Directory selection
   - Extension management
   - Scan button
   - Progress bar

7. **`paste_widget.py`** - Extract Paste tab:
   - Extract from old code (lines ~700-900)
   - JSON file selection
   - Output directory selection
   - Recreate button
   - Progress bar

8. **`extension_manager.py`** - Extension list management:
   - Add/remove extensions
   - Save to settings

### Priority 2: Main Entry Point
9. **`main.py`** - New application entry point:
   ```python
   import sys
   from PySide6.QtWidgets import QApplication
   from src.di_container import DIContainer
   from src.presentation.views.main_window import MainWindow
   from src.infrastructure.logging import setup_logger
   
   def main():
       # Setup logging
       logger = setup_logger('sagittarius_entj')
       logger.info("Starting Sagittarius ENTJ...")
       
       # Create DI container
       container = DIContainer()
       
       # Create Qt application
       app = QApplication(sys.argv)
       app.setApplicationName("Sagittarius ENTJ")
       app.setOrganizationName("HoangAnhTran")
       
       # Create main window
       window = MainWindow(container)
       window.show()
       
       sys.exit(app.exec())
   
   if __name__ == "__main__":
       main()
   ```

### Priority 3: Unit Tests
10. **`tests/unit/domain/test_snapshot.py`**:
    ```python
    def test_snapshot_creation():
        snapshot = DirectorySnapshot(root_path="/test")
        assert snapshot.get_file_count() == 0
    
    def test_snapshot_add_file():
        snapshot = DirectorySnapshot(root_path="/test")
        file = FileEntry(relative_path="test.txt", content=b"hello")
        snapshot.add_file(file)
        assert snapshot.get_file_count() == 1
    ```

11. **`tests/unit/domain/test_file_entry.py`**
12. **`tests/unit/domain/test_extension_filter.py`**
13. **`tests/unit/application/test_scan_use_case.py`** (with mocks)
14. **`tests/unit/infrastructure/test_base64_encoder.py`**

### Priority 4: Integration Tests
15. **`tests/integration/test_full_scan_flow.py`**:
    ```python
    def test_full_scan_save_load_recreate(tmp_path):
        # Scan directory
        # Save snapshot
        # Load snapshot
        # Recreate directory
        # Verify files match
    ```

### Priority 5: Build Configuration
16. **Update `Sagittarius-ENTJ.spec`**:
    - Change entry point to `main.py`
    - Include new `src/` package
    - Update `datas` and `hiddenimports`

17. **Update `buildExe.ps1`** (if needed)

### Priority 6: Documentation
18. **Update `README.md`**:
    - New architecture section
    - Development setup instructions
    - Testing instructions

19. **Create `docs/api.md`** - API documentation for each layer

## 📋 Step-by-Step Migration Process

### Step 1: Read Old Code
```powershell
# Read the old Sagittarius-ENTJ.py to understand UI structure
Get-Content Sagittarius-ENTJ.py | Select-Object -First 50
```

### Step 2: Extract WorkerSignals and AsyncWorker
- Copy from lines ~125-135 (WorkerSignals)
- Create `src/presentation/workers/worker_signals.py`
- Create `src/presentation/workers/async_worker.py`

### Step 3: Extract ViewModel Logic
- Lines ~150-600: ViewModel class
- Split into `copy_view_model.py` and `paste_view_model.py`
- Replace old `Model` calls with Use Case calls
- Remove direct file I/O, use Use Cases instead

### Step 4: Extract UI Widgets
- Lines ~600-1100: View class
- Split into `main_window.py`, `copy_widget.py`, `paste_widget.py`
- Connect to ViewModels instead of ViewModel directly

### Step 5: Create main.py
- Lines ~1100-1164: Main entry point
- Clean it up, use DI container

### Step 6: Test Each Component
- Write unit tests as you extract
- Test in isolation with mocks

### Step 7: Update Build
- Modify `.spec` file
- Test executable build

## 🧪 Testing Strategy

### Unit Test Example
```python
# tests/unit/application/test_scan_use_case.py
from unittest.mock import Mock, MagicMock
from src.application.use_cases.scan_directory import ScanDirectoryUseCase
from src.application.dto.scan_request import ScanRequest

def test_scan_directory_use_case():
    # Arrange
    mock_fs = Mock()
    mock_fs.directory_exists.return_value = True
    mock_fs.list_files.return_value = ['/test/file1.py', '/test/file2.py']
    mock_fs.read_file.return_value = b"content"
    
    mock_encoder = Mock()
    mock_encoder.encode.return_value = "encoded_content"
    
    use_case = ScanDirectoryUseCase(mock_fs, mock_encoder)
    request = ScanRequest(root_path="/test", extensions=['.py'])
    
    # Act
    snapshot = use_case.execute(request)
    
    # Assert
    assert snapshot.get_file_count() == 2
    assert snapshot.root_path == "/test"
```

## 🔧 Useful Commands

### Run Tests
```powershell
# Install pytest
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

### Build Executable
```powershell
# Run build script
.\buildExe.ps1
```

### Check Imports
```powershell
# Find import errors
python -m src.domain.models.snapshot
```

## ⚠️ Common Pitfalls

1. **Circular Imports**: 
   - Use `TYPE_CHECKING` for type hints
   - Import at function level if needed

2. **Qt Dependency in Domain**: 
   - NEVER import PySide6 in Domain/Application layers
   - Keep it in Presentation/Infrastructure only

3. **Missing __init__.py**: 
   - Every directory needs `__init__.py`
   - Export key classes in `__init__.py`

4. **Forgetting to Encode**: 
   - FileEntry needs `set_encoded_content()` before serialization

5. **Not Using DI Container**: 
   - Always get dependencies from container
   - Don't create instances directly in UI

## 📚 Reference

### Old Code Mapping
| Old Code | New Location |
|----------|-------------|
| `Model` class | Split into Use Cases + Repositories |
| `Model.scan_directory()` | `ScanDirectoryUseCase.execute()` |
| `Model.save_database()` | `SaveSnapshotUseCase.execute()` |
| `Model.load_database()` | `LoadSnapshotUseCase.execute()` |
| `Model.recreate_from_database()` | `RecreateDirectoryUseCase.execute()` |
| `ViewModel` class | Split into `CopyViewModel` + `PasteViewModel` |
| `WorkerSignals` class | `src/presentation/workers/worker_signals.py` |
| `View` class | `MainWindow` + `CopyWidget` + `PasteWidget` |

### Import Examples
```python
# Domain layer - NO external dependencies
from src.domain.models.snapshot import DirectorySnapshot
from src.domain.services.extension_filter import ExtensionFilter

# Application layer - Use domain only
from src.application.use_cases.scan_directory import ScanDirectoryUseCase
from src.application.dto.scan_request import ScanRequest

# Infrastructure - External dependencies OK
from PySide6.QtCore import QSettings  # OK here
from src.infrastructure.persistence.settings_repository import SettingsRepository

# Presentation - Qt/PySide6 OK
from PySide6.QtWidgets import QWidget, QPushButton
from src.di_container import DIContainer
```

## ✅ Checklist

- [ ] Extract WorkerSignals
- [ ] Extract AsyncWorker
- [ ] Create CopyViewModel
- [ ] Create PasteViewModel
- [ ] Create MainWindow
- [ ] Create CopyWidget
- [ ] Create PasteWidget
- [ ] Create ExtensionManager
- [ ] Create main.py
- [ ] Write domain unit tests
- [ ] Write application unit tests
- [ ] Write integration tests
- [ ] Update .spec file
- [ ] Update buildExe.ps1
- [ ] Update README.md
- [ ] Test executable build
- [ ] Verify all features work

## 🎉 Success Criteria

1. ✅ All old features working
2. ✅ Executable builds successfully
3. ✅ Unit test coverage > 80%
4. ✅ No circular dependencies
5. ✅ Domain layer has ZERO Qt dependencies
6. ✅ All code follows PEP 8
7. ✅ Documentation updated

## 📞 Need Help?

If you get stuck:
1. Check `docs/architecture.md` for design overview
2. Look at existing code in Domain/Application layers as examples
3. Run tests frequently to catch issues early
4. Use `pytest` with `-v` flag for detailed output

Good luck with the migration! 🚀
