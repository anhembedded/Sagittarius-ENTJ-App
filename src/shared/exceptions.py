"""Custom exceptions for Sagittarius ENTJ."""


class SagittariusException(Exception):
    """Base exception for all Sagittarius ENTJ errors."""
    pass


class DomainException(SagittariusException):
    """Base exception for domain-related errors."""
    pass


class ValidationError(DomainException):
    """Raised when validation fails."""
    pass


class FileSystemError(SagittariusException):
    """Raised when file system operations fail."""
    pass


class EncodingError(SagittariusException):
    """Raised when encoding/decoding fails."""
    pass


class RepositoryError(SagittariusException):
    """Raised when repository operations fail."""
    pass


class SnapshotNotFoundError(RepositoryError):
    """Raised when a snapshot cannot be found."""
    pass


class InvalidSnapshotError(ValidationError):
    """Raised when a snapshot is invalid or corrupted."""
    pass
