"""Type definitions for internacia SDK data structures.

Every column in internacia-db is nullable, so nested lists and structs are
typed ``Optional``. Enum-like string columns (``status``, ``scope_category``,
``geographic_scope``, ...) are open: new values may appear in any MINOR
release of the data, so they are typed ``str`` rather than ``Literal``.
"""

from typing import TypedDict


class CapitalCity(TypedDict, total=False):
    """Capital city information."""

    name: str | None
    lng: float | None
    lat: float | None


class Region(TypedDict, total=False):
    """World Bank region information."""

    id: str | None
    value: str | None


class IncomeLevel(TypedDict, total=False):
    """World Bank income level information."""

    id: str | None
    value: str | None


class Language(TypedDict, total=False):
    """Language information."""

    code: str | None
    name: str | None
    official: bool | None


class Currency(TypedDict, total=False):
    """Currency information."""

    code: str | None
    name: str | None
    symbol: str | None


class NativeName(TypedDict, total=False):
    """Native name information."""

    official: str | None
    common: str | None


class OtherName(TypedDict, total=False):
    """Name in another language, keyed by language code in ``id``."""

    id: str | None
    name: str | None


class Country(TypedDict, total=False):
    """Country data structure."""

    code: str | None
    name: str | None
    iso3code: str | None
    numeric_code: str | None
    official_name: str | None
    capital_city: CapitalCity | None
    region: Region | None
    incomeLevel: IncomeLevel | None
    languages: list[Language] | None
    currencies: list[Currency] | None
    un_member: bool | None
    independent: bool | None
    continents: list[str] | None
    borders: list[str] | None
    native_names: dict[str, NativeName] | None
    other_names: list[OtherName] | None
    # Additional fields may exist in the database


class Acronym(TypedDict, total=False):
    """Acronym information."""

    lang: str | None
    value: str | None


class Topic(TypedDict, total=False):
    """Topic information."""

    key: str | None
    name: str | None


class Member(TypedDict, total=False):
    """Member country information."""

    id: str | None
    name: str | None
    type: str | None
    status: str | None
    joined: str | None
    left: str | None
    role: str | None
    note: str | None


class Intblock(TypedDict, total=False):
    """International block data structure."""

    id: str | None
    name: str | None
    blocktype: list[str] | None
    status: str | None
    other_names: list[OtherName] | None
    acronyms: list[Acronym] | None
    includes: list[Member] | None
    founded: str | None
    geographic_scope: str | None
    scope_category: str | None
    tags: list[str] | None
    topics: list[Topic] | None
    # Additional fields may exist in the database


class SearchResult(TypedDict, total=False):
    """Search result with type indicator."""

    type: str  # 'country' or 'intblock'
    # All fields from Country or Intblock depending on type
