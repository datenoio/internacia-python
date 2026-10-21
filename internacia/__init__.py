"""
Internacia Python SDK

A Python SDK for accessing internacia-db data with support for countries,
international blocks, and fuzzy search across multiple languages.
"""

from internacia.client import InternaciaClient
from internacia.downloader import (
    check_for_updates,
    download_database,
    get_cache_dir,
    get_cached_database_path,
    get_latest_version,
    list_releases,
)
from internacia.exceptions import (
    DatabaseError,
    DownloadError,
    InternaciaError,
    NotFoundError,
    ValidationError,
    VersionError,
)
from internacia.models import (
    Acronym,
    CapitalCity,
    Country,
    Currency,
    IncomeLevel,
    Intblock,
    Language,
    Member,
    NativeName,
    OtherName,
    Region,
    SearchResult,
    Topic,
)
from internacia.version import __version__

__all__ = [
    "InternaciaClient",
    "__version__",
    "InternaciaError",
    "DatabaseError",
    "NotFoundError",
    "ValidationError",
    "DownloadError",
    "VersionError",
    "Country",
    "Intblock",
    "SearchResult",
    "CapitalCity",
    "Region",
    "IncomeLevel",
    "Language",
    "Currency",
    "NativeName",
    "OtherName",
    "Acronym",
    "Topic",
    "Member",
    "download_database",
    "get_latest_version",
    "check_for_updates",
    "list_releases",
    "get_cache_dir",
    "get_cached_database_path",
]
