"""Application-wide constants."""

from typing import List

# Application metadata
APP_NAME = "Sagittarius ENTJ"
APP_VERSION = "2.0.0"
APP_ORGANIZATION = "HoangAnhTran"

# Default file extensions
DEFAULT_EXTENSIONS: List[str] = ['.txt', '.py', '.md', '.cpp', '.h', '.hpp', '.c']

# Settings keys
SETTINGS_EXTENSIONS = "extensions"
SETTINGS_COPY_SOURCE_DIR = "paths/copySourceDir"
SETTINGS_COPY_JSON_PATH = "paths/copyJsonPath"
SETTINGS_PASTE_JSON_PATH = "paths/pasteJsonPath"
SETTINGS_PASTE_OUTPUT_DIR = "paths/pasteOutputDir"

# File system
MAX_FILE_SIZE_MB = 100  # Maximum file size to encode (in MB)
BUFFER_SIZE = 65536  # 64KB buffer for file reading

# Progress reporting
PROGRESS_UPDATE_INTERVAL_MS = 100  # Update UI every 100ms

# Logging
LOG_FORMAT = "[%(asctime)s] %(levelname)s - %(name)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
