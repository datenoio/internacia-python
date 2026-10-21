"""Custom exceptions for internacia SDK."""


class InternaciaError(Exception):
    """Base exception for internacia SDK."""


class DatabaseError(InternaciaError):
    """Database-related errors."""


class NotFoundError(InternaciaError):
    """Resource not found errors."""


class ValidationError(InternaciaError):
    """Input validation errors."""


class DownloadError(InternaciaError):
    """Database download-related errors."""


class VersionError(InternaciaError):
    """Version-related errors."""


class ContractError(VersionError):
    """The database's data contract is not supported by this SDK."""
