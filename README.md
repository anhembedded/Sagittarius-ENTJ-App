# Sagittarius-ENTJ - Directory Snapshot Manager 🏹📁

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/Python-3.6%2B-blue.svg)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/PySide6-6.4%2B-green.svg)](https://doc.qt.io/qtforpython/)

A powerful directory snapshot tool for structured data management, designed for efficient directory replication and archival operations.

## Features ✨
- **Dual Operation Modes**
  - 🧹 Clean Copy: Create structured JSON snapshots
  - 🎯 Precision Paste: Recreate directory structures
- **Advanced Configuration**
  - Custom file extension filters
  - Base64 file content encoding
- **Security**
  - 🔐 Password-protected encryption (AES-256-GCM)
  - Optional snapshot encryption with strong authentication
  - Secure key derivation using PBKDF2-HMAC-SHA256
- **Enterprise-Grade Architecture**
  - MVVM pattern implementation
  - Asynchronous operations
  - Cross-platform compatibility
- **Enhanced Security**
  - Content validation
  - Error-resistant operations
  - Transactional logging

## System Requirements 💻
- Python 3.6+
- Qt/PySide6 framework
- 50MB disk space minimum
- Read/write permissions for target directories

## Installation 🛠️
```bash
# Clone repository
git clone https://github.com/yourusername/Sagittarius-ENTJ.git
cd Sagittarius-ENTJ

# Install dependencies
pip install -r requirements.txt
```

## Usage 🚀

### Creating an Encrypted Snapshot
1. Open the "Copy" tab
2. Select the source directory to snapshot
3. Choose output JSON file location
4. ✅ Check "🔐 Enable Encryption" for password protection
5. Click "📸 Create Snapshot"
6. Enter and confirm your password
7. Snapshot will be encrypted with AES-256-GCM

### Loading an Encrypted Snapshot
1. Open the "Paste" tab
2. Click "📂 Load Snapshot" and select the encrypted JSON file
3. Enter the password when prompted
4. Select output directory
5. Click "📂 Restore Directory"

**Note**: Encrypted snapshots are not human-readable and require the original password to decrypt.
