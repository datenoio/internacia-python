"""Type definitions for internacia SDK data structures.

Every column in internacia-db is nullable, so nested lists and structs are
typed ``Optional``. Enum-like string columns (``status``, ``scope_category``,
``geographic_scope``, ...) are open: new values may appear in any MINOR
release of the data, so they are typed ``str`` rather than ``Literal``.
"""

from typing import Dict, List, Optional, TypedDict


class CapitalCity(TypedDict, total=False):
    """Capital city information."""
    name: Optional[str]
    lng: Optional[float]
    lat: Optional[float]


class Region(TypedDict, total=False):
    """World Bank region information."""
    id: Optional[str]
    value: Optional[str]


class IncomeLevel(TypedDict, total=False):
    """World Bank income level information."""
    id: Optional[str]
    value: Optional[str]


class Language(TypedDict, total=False):
    """Language information."""
    code: Optional[str]
    name: Optional[str]
    official: Optional[bool]


class Currency(TypedDict, total=False):
    """Currency information."""
    code: Optional[str]
    name: Optional[str]
    symbol: Optional[str]


class NativeName(TypedDict, total=False):
    """Native name information."""
    official: Optional[str]
    common: Optional[str]


class OtherName(TypedDict, total=False):
    """Name in another language, keyed by language code in ``id``."""
    id: Optional[str]
    name: Optional[str]


class Country(TypedDict, total=False):
    """Country data structure."""
    code: Optional[str]
    name: Optional[str]
    iso3code: Optional[str]
    numeric_code: Optional[str]
    official_name: Optional[str]
    capital_city: Optional[CapitalCity]
    region: Optional[Region]
    incomeLevel: Optional[IncomeLevel]
    languages: Optional[List[Language]]
    currencies: Optional[List[Currency]]
    un_member: Optional[bool]
    independent: Optional[bool]
    continents: Optional[List[str]]
    borders: Optional[List[str]]
    native_names: Optional[Dict[str, NativeName]]
    other_names: Optional[List[OtherName]]
    # Additional fields may exist in the database


class Acronym(TypedDict, total=False):
    """Acronym information."""
    lang: Optional[str]
    value: Optional[str]


class Topic(TypedDict, total=False):
    """Topic information."""
    key: Optional[str]
    name: Optional[str]


class Member(TypedDict, total=False):
    """Member country information."""
    id: Optional[str]
    name: Optional[str]
    type: Optional[str]
    status: Optional[str]
    joined: Optional[str]
    left: Optional[str]
    role: Optional[str]
    note: Optional[str]


class Intblock(TypedDict, total=False):
    """International block data structure."""
    id: Optional[str]
    name: Optional[str]
    blocktype: Optional[List[str]]
    status: Optional[str]
    other_names: Optional[List[OtherName]]
    acronyms: Optional[List[Acronym]]
    includes: Optional[List[Member]]
    founded: Optional[str]
    geographic_scope: Optional[str]
    scope_category: Optional[str]
    tags: Optional[List[str]]
    topics: Optional[List[Topic]]
    # Additional fields may exist in the database


class SearchResult(TypedDict, total=False):
    """Search result with type indicator."""
    type: str  # 'country' or 'intblock'
    # All fields from Country or Intblock depending on type
