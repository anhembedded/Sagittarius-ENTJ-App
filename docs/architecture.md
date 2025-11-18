# Sagittarius ENTJ - Architecture Documentation

## Overview

Sagittarius ENTJ is refactored using **Clean Architecture** principles with clear separation of concerns across multiple layers.

## Architecture Layers

### 1. Domain Layer (Business Logic)
- **Purpose**: Core business logic, framework-agnostic
- **Location**: `src/domain/`
- **Key Components**:
  - **Models**: `DirectorySnapshot`, `FileEntry`, `DirectoryEntry`
  - **Services**: `ExtensionFilter`
  - **Interfaces**: `IContentEncoder`, `ISnapshotRepository`, `IFileSystemService`
- **Rules**:
  - NO dependencies on external frameworks (Qt, PySide6)
  - Pure Python, easily testable
  - Defines interfaces for external dependencies

### 2. Application Layer (Use Cases)
- **Purpose**: Orchestrates business workflows
- **Location**: `src/application/`
- **Key Components**:
  - **Use Cases**: `ScanDirectoryUseCase`, `SaveSnapshotUseCase`, `LoadSnapshotUseCase`, `RecreateDirectoryUseCase`
  - **DTOs**: `ScanRequest`, `RecreateRequest`
- **Rules**:
  - Depends on Domain Layer only
  - NO UI code
  - Each use case represents one business operation

### 3. Infrastructure Layer (External Dependencies)
- **Purpose**: Implements technical capabilities
- **Location**: `src/infrastructure/`
- **Key Components**:
  - **Encoding**: `Base64Encoder`
  - **File System**: `FileSystemService`
  - **Persistence**: `JsonSnapshotRepository`, `SettingsRepository`
  - **Logging**: Application logger setup
- **Rules**:
  - Implements Domain interfaces
  - Handles external I/O (files, settings, JSON)

### 4. Presentation Layer (UI)
- **Purpose**: User interface components
- **Location**: `src/presentation/`
- **Key Components**:
  - **Views**: `MainWindow`, `CopyWidget`, `PasteWidget`
  - **ViewModels**: Manage UI state and logic
  - **Workers**: Async operations using Qt QThreadPool
- **Rules**:
  - Depends on Application Layer (Use Cases)
  - Qt/PySide6 specific code only here
  - Thin layer, delegates to Use Cases

## Dependency Flow

```
Presentation -> Application -> Domain <- Infrastructure
```

- **Presentation** calls **Application** (Use Cases)
- **Application** uses **Domain** (Business Logic)
- **Infrastructure** implements **Domain** interfaces
- **Domain** knows NOTHING about outer layers

## Key Design Patterns

### 1. Repository Pattern
- `ISnapshotRepository` interface in Domain
- `JsonSnapshotRepository` implementation in Infrastructure
- Easy to swap (e.g., SQLite, Cloud Storage)

### 2. Dependency Injection
- `DIContainer` class manages all dependencies
- Centralized dependency creation
- Easy mocking for tests

### 3. Use Case Pattern
- Each business operation is a separate class
- Clear input/output contracts (DTOs)
- Testable in isolation

### 4. Interface Segregation
- Small, focused interfaces
- `IContentEncoder`, `IFileSystemService`, `ISnapshotRepository`
- Easy to implement and mock

## Benefits

### 1. Testability
```python
# Mock dependencies easily
mock_fs = MockFileSystemService()
use_case = ScanDirectoryUseCase(mock_fs, mock_encoder)
result = use_case.execute(request)
```

### 2. Maintainability
- Each layer has single responsibility
- Changes in one layer don't affect others
- Clear boundaries

### 3. Extensibility
- Add new encoders (Gzip, Encryption)
- Add new storage (Cloud, Database)
- Add new UI frameworks (Web, CLI)

### 4. Framework Independence
- Domain logic can be ported to other languages
- UI can be swapped (Qt -> Web)
- Business rules stay the same

## Testing Strategy

### Unit Tests
- Domain models and services (pure logic)
- Use cases with mocked dependencies
- Infrastructure implementations

### Integration Tests
- Full workflows (scan -> save -> load -> recreate)
- Real file system operations
- End-to-end scenarios

### Test Location
- `tests/unit/domain/` - Domain layer tests
- `tests/unit/application/` - Use case tests
- `tests/integration/` - Full workflow tests

## Migration from Old Code

The old 1164-line `Sagittarius-ENTJ.py` has been split into:
- **Domain**: 8 files (~400 lines)
- **Application**: 7 files (~300 lines)
- **Infrastructure**: 8 files (~400 lines)
- **Presentation**: TO BE CREATED (~500 lines)
- **Tests**: TO BE CREATED (~300 lines)

Total: ~1900 lines with much better organization, testability, and maintainability.

## Next Steps

1. ✅ Domain Layer implemented
2. ✅ Application Layer implemented
3. ✅ Infrastructure Layer implemented
4. 🔄 Presentation Layer (IN PROGRESS)
5. ⏳ Unit Tests
6. ⏳ Integration Tests
7. ⏳ Update build scripts
8. ⏳ Documentation updates

## API Usage Example

```python
# Setup DI Container
container = DIContainer()

# Scan a directory
scan_use_case = container.get_scan_directory_use_case()
request = ScanRequest(
    root_path="/path/to/scan",
    extensions=['.py', '.txt']
)
snapshot = scan_use_case.execute(request)

# Save snapshot
save_use_case = container.get_save_snapshot_use_case()
save_use_case.execute(snapshot, "/path/to/output.json")

# Load and recreate
load_use_case = container.get_load_snapshot_use_case()
snapshot = load_use_case.execute("/path/to/output.json")

recreate_use_case = container.get_recreate_directory_use_case()
recreate_request = RecreateRequest(
    snapshot=snapshot,
    output_path="/path/to/recreate"
)
recreate_use_case.execute(recreate_request)
```
