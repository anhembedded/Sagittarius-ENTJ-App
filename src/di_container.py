"""Dependency Injection Container."""

from typing import Optional

from .domain.interfaces.encoder import IContentEncoder
from .domain.interfaces.file_system import IFileSystemService
from .domain.interfaces.repository import ISnapshotRepository
from .domain.interfaces.encryption import IEncryptionService
from .domain.services.extension_filter import ExtensionFilter

from .infrastructure.encoding.base64_encoder import Base64Encoder
from .infrastructure.encryption.aes_gcm_encryptor import AESGCMEncryptor
from .infrastructure.file_system.file_system_service import FileSystemService
from .infrastructure.persistence.json_repository import JsonSnapshotRepository
from .infrastructure.persistence.settings_repository import SettingsRepository

from .application.use_cases.scan_directory import ScanDirectoryUseCase
from .application.use_cases.save_snapshot import SaveSnapshotUseCase
from .application.use_cases.load_snapshot import LoadSnapshotUseCase
from .application.use_cases.recreate_directory import RecreateDirectoryUseCase


class DIContainer:
    """Dependency Injection Container for the application."""
    
    def __init__(self):
        """Initialize the DI container with all dependencies."""
        # Infrastructure layer (Singletons)
        self._encoder: Optional[IContentEncoder] = None
        self._encryption_service: Optional[IEncryptionService] = None
        self._file_system: Optional[IFileSystemService] = None
        self._snapshot_repository: Optional[ISnapshotRepository] = None
        self._settings_repository: Optional[SettingsRepository] = None
        
        # Domain services
        self._extension_filter: Optional[ExtensionFilter] = None
    
    # Infrastructure getters (Singleton pattern)
    
    def get_encoder(self) -> IContentEncoder:
        """Get content encoder instance."""
        if self._encoder is None:
            self._encoder = Base64Encoder()
        return self._encoder
    
    def get_file_system(self) -> IFileSystemService:
        """Get file system service instance."""
        if self._file_system is None:
            self._file_system = FileSystemService()
        return self._file_system
    
    def get_encryption_service(self) -> IEncryptionService:
        """Get encryption service instance."""
        if self._encryption_service is None:
            self._encryption_service = AESGCMEncryptor()
        return self._encryption_service
    
    def get_snapshot_repository(self) -> ISnapshotRepository:
        """Get snapshot repository instance."""
        if self._snapshot_repository is None:
            encoder = self.get_encoder()
            encryption = self.get_encryption_service()
            self._snapshot_repository = JsonSnapshotRepository(encoder, encryption)
        return self._snapshot_repository
    
    def get_settings_repository(self) -> SettingsRepository:
        """Get settings repository instance."""
        if self._settings_repository is None:
            self._settings_repository = SettingsRepository()
        return self._settings_repository
    
    def get_extension_filter(self) -> ExtensionFilter:
        """Get extension filter instance."""
        if self._extension_filter is None:
            # Load extensions from settings
            settings = self.get_settings_repository()
            extensions = settings.get_list('extensions')
            self._extension_filter = ExtensionFilter(extensions if extensions else None)
        return self._extension_filter
    
    # Use case factories (New instance each time)
    
    def get_scan_directory_use_case(self) -> ScanDirectoryUseCase:
        """Create a new scan directory use case."""
        return ScanDirectoryUseCase(
            file_system=self.get_file_system(),
            encoder=self.get_encoder()
        )
    
    def get_save_snapshot_use_case(self) -> SaveSnapshotUseCase:
        """Create a new save snapshot use case."""
        return SaveSnapshotUseCase(
            repository=self.get_snapshot_repository()
        )
    
    def get_load_snapshot_use_case(self) -> LoadSnapshotUseCase:
        """Create a new load snapshot use case."""
        return LoadSnapshotUseCase(
            repository=self.get_snapshot_repository()
        )
    
    def get_recreate_directory_use_case(self) -> RecreateDirectoryUseCase:
        """Create a new recreate directory use case."""
        return RecreateDirectoryUseCase(
            file_system=self.get_file_system()
        )
