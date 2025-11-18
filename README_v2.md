# 🎯 Sagittarius ENTJ - Directory Snapshot Manager v2.0

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.4%2B-green.svg)](https://doc.qt.io/qtforpython/)

A powerful, refactored directory snapshot tool built with Clean Architecture principles. Create, save, and restore complete directory structures with file contents encoded in JSON format.

## ✨ What's New in v2.0

- **🏗️ Clean Architecture**: Complete separation of concerns across 4 layers
- **🧪 Testable**: 80%+ unit test coverage with mock-based testing
- **🔧 Modular**: Easy to extend with new features
- **📦 Dependency Injection**: Centralized dependency management
- **🎯 SOLID Principles**: Following best practices throughout
- **📚 Well-Documented**: Comprehensive documentation and diagrams

## 🎨 Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Presentation Layer (UI)                    │
│  MainWindow, CopyWidget, PasteWidget, ViewModels        │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│         Application Layer (Use Cases)                   │
│  ScanDirectory, SaveSnapshot, LoadSnapshot, Recreate    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│           Domain Layer (Business Logic)                 │
│  Snapshot, FileEntry, DirectoryEntry, Interfaces        │
└─────────────────────────────────────────────────────────┘
                         ↑
┌─────────────────────────────────────────────────────────┐
│        Infrastructure Layer (Technical)                 │
│  FileSystem, JsonRepository, Base64Encoder, Settings    │
└─────────────────────────────────────────────────────────┘
```

See [docs/architecture.md](docs/architecture.md) for detailed architecture documentation.

## 🚀 Features

### Core Functionality
- ✅ **Snapshot Creation**: Scan directories and encode file contents
- ✅ **JSON Export**: Save snapshots in portable JSON format
- ✅ **Directory Recreation**: Restore directory structures from snapshots
- ✅ **Extension Filtering**: Configure which file types to include
- ✅ **Progress Tracking**: Real-time progress updates with visual feedback
- ✅ **Error Handling**: Robust error handling and validation
- ✅ **Settings Persistence**: Remembers your paths and preferences

### Technical Features
- 🎯 **Clean Architecture**: Domain-driven design with clear boundaries
- 🧪 **Unit Tested**: Comprehensive test suite with pytest
- 🔌 **Dependency Injection**: Easy to mock and test
- 📦 **Modular Design**: Add new features without breaking existing code
- 🌐 **Cross-Platform**: Works on Windows, macOS, and Linux
- 🎨 **Modern UI**: Built with PySide6/Qt6

## 📋 Requirements

- Python 3.8 or higher
- PySide6 (Qt for Python)
- 50MB disk space minimum

## 🛠️ Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/anhembedded/Sagittarius-ENTJ-App.git
cd Sagittarius-ENTJ-App

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### For Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run tests with coverage
pytest --cov=src tests/

# Build executable
pyinstaller Sagittarius-ENTJ.spec
```

## 📖 Usage

### 1. Create a Snapshot

1. Open the **Snapshot (Copy)** tab
2. Click **Browse** next to "Source Directory" and select the folder to snapshot
3. Click **Browse** next to "Output JSON File" and choose where to save the snapshot
4. Click **📸 Create Snapshot**
5. Wait for the operation to complete

### 2. Configure Extensions

1. Open the **Extensions** tab
2. Add file extensions you want to include (e.g., `.py`, `.txt`, `.cpp`)
3. Remove extensions you don't need
4. Click **Reset to Defaults** to restore default extensions

### 3. Restore a Snapshot

1. Open the **Restore (Paste)** tab
2. Click **Browse** next to "Input JSON File" and select your snapshot
3. Click **📂 Load Snapshot** to preview snapshot details
4. Click **Browse** next to "Output Directory" and choose where to restore
5. Click **📂 Restore Directory**
6. Confirm the operation

## 🏗️ Project Structure

```
Sagittarius-ENTJ-App/
├── main.py                 # Application entry point
├── src/
│   ├── domain/            # Pure business logic (framework-agnostic)
│   │   ├── models/        # DirectorySnapshot, FileEntry, DirectoryEntry
│   │   ├── services/      # ExtensionFilter
│   │   └── interfaces/    # Abstract interfaces
│   ├── application/       # Use cases and orchestration
│   │   ├── use_cases/     # ScanDirectory, SaveSnapshot, LoadSnapshot, Recreate
│   │   └── dto/           # Data Transfer Objects
│   ├── infrastructure/    # External dependencies
│   │   ├── persistence/   # JsonRepository, SettingsRepository
│   │   ├── file_system/   # FileSystemService
│   │   ├── encoding/      # Base64Encoder
│   │   └── logging/       # Logger setup
│   ├── presentation/      # UI layer (PySide6)
│   │   ├── views/         # MainWindow, CopyWidget, PasteWidget
│   │   ├── view_models/   # CopyViewModel, PasteViewModel
│   │   └── workers/       # Async workers
│   ├── shared/           # Cross-cutting concerns
│   └── di_container.py   # Dependency injection
├── tests/                # Test suite
│   ├── unit/            # Unit tests
│   └── integration/     # Integration tests
├── docs/                # Documentation
│   ├── architecture.md  # Architecture guide
│   ├── MIGRATION_GUIDE.md
│   └── diagrams/        # PlantUML diagrams
├── requirements.txt     # Production dependencies
└── requirements-dev.txt # Development dependencies
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/domain/test_snapshot.py

# Run tests in watch mode
pytest-watch
```

## 🔧 Building Executable

```bash
# Build executable with PyInstaller
pyinstaller Sagittarius-ENTJ.spec

# Or use the build script (Windows)
.\buildExe.ps1

# Executable will be in: executable/Sagittarius-ENTJ.exe
```

## 📚 Documentation

- [Architecture Overview](docs/architecture.md) - Detailed architecture explanation
- [Migration Guide](docs/MIGRATION_GUIDE.md) - Guide for understanding the refactoring
- [API Documentation](docs/api.md) - API reference (coming soon)
- [PlantUML Diagrams](docs/diagrams/) - Architecture and sequence diagrams

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for your changes
4. Ensure all tests pass (`pytest`)
5. Commit your changes (`git commit -m 'feat: add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `refactor:` - Code refactoring
- `docs:` - Documentation changes
- `test:` - Test changes
- `build:` - Build system changes

## 🐛 Known Issues

- None currently. Please report any issues you find!

## 📝 Changelog

### v2.0.0 (2025-11-18)
- Complete architecture refactoring
- Implemented Clean Architecture with 4 layers
- Added comprehensive unit tests
- Improved error handling and validation
- Added dependency injection container
- Updated to modern PySide6 UI
- Added extensive documentation

### v1.0.0
- Initial release
- Basic snapshot and restore functionality

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Hoang Anh Tran**
- Email: Anh.Embedded@gmail.com
- GitHub: [@anhembedded](https://github.com/anhembedded)

## 🙏 Acknowledgments

- Built with [PySide6](https://doc.qt.io/qtforpython/)
- Packaged with [PyInstaller](https://pyinstaller.org/)
- Tested with [pytest](https://pytest.org/)

---

**⭐ If you find this project useful, please consider giving it a star!**
