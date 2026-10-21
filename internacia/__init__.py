"""
Internacia Python SDK

A Python SDK for accessing internacia-db data with support for countries,
international blocks, and fuzzy search across multiple languages.
"""

import logging

from internacia.client import InternaciaClient
from internacia.contract import SUPPORTED_CONTRACT_MAJOR, TESTED_CONTRACT
from internacia.downloader import (
    cached_versions,
    check_for_updates,
    download_database,
    get_cache_dir,
    get_cached_database_path,
    get_latest_version,
    list_releases,
)
from internacia.exceptions import (
    ContractError,
    DatabaseError,
    DownloadError,
    InternaciaError,
    NotFoundError,
    ValidationError,
    VersionError,
)
from internacia.models import (
    Acronym,
    Blocktype,
    CapitalCity,
    Country,
    Currency,
    CurrencyEntry,
    IdResolution,
    IncomeLevel,
    Intblock,
    Language,
    LanguageEntry,
    Member,
    Membership,
    NativeName,
    OtherName,
    Region,
    RegionEntry,
    SearchResult,
    TimezoneEntry,
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
    "ContractError",
    "SUPPORTED_CONTRACT_MAJOR",
    "TESTED_CONTRACT",
    "cached_versions",
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
    "Membership",
    "Blocktype",
    "IdResolution",
    "CurrencyEntry",
    "LanguageEntry",
    "TimezoneEntry",
    "RegionEntry",
    "download_database",
    "get_latest_version",
    "check_for_updates",
    "list_releases",
    "get_cache_dir",
    "get_cached_database_path",
]

logging.getLogger(__name__).addHandler(logging.NullHandler())
