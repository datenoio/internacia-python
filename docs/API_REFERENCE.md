# Internacia Python SDK - API Reference

Complete API reference for the Internacia Python SDK.

## Table of Contents

- [InternaciaClient](#internaciaclient)
- [CountriesClient](#countriesclient)
- [IntblocksClient](#intblocksclient)
- [SearchClient](#searchclient)
- [Downloader Functions](#downloader-functions)
- [Data Models](#data-models)
- [Exceptions](#exceptions)

---

## InternaciaClient

Main client class for accessing internacia-db data.

### Constructor

```python
InternaciaClient(
    db_path: Optional[Path] = None,
    data_dir: Optional[Path] = None
)
```

**Parameters:**
- `db_path` (Optional[Path]): Path to the DuckDB database file. If `None`, the SDK will attempt to find it in the default location or via environment variables.
- `data_dir` (Optional[Path]): Path to the internacia-db data directory (currently unused, reserved for future use).

**Raises:**
- `FileNotFoundError`: If the database file cannot be found at the specified or default location.

**Example:**
```python
from internacia import InternaciaClient
from pathlib import Path

# Use default database location
client = InternaciaClient()

# Use custom database path
client = InternaciaClient(db_path=Path("/path/to/internacia.duckdb"))
```

**Attributes:**
- `countries` (CountriesClient): Client for querying countries data
- `intblocks` (IntblocksClient): Client for querying international blocks data
- `search` (SearchClient): Client for searching countries and blocks

---

## CountriesClient

Client for querying countries data.

### Methods

#### `get_by_code(code: str) -> Optional[Country]`

Get a country by its ISO 3166-1 alpha-2 code.

**Parameters:**
- `code` (str): Two-letter country code (e.g., "US", "FR", "GB")

**Returns:**
- `Optional[Country]`: Country data as a dictionary, or `None` if not found

**Raises:**
- `ValidationError`: If code is not a valid 2-letter alphabetic string

**Example:**
```python
country = client.countries.get_by_code("US")
if country:
    print(country["name"])  # "United States"
```

---

#### `get_by_iso3(iso3code: str) -> Optional[Country]`

Get a country by its ISO 3166-1 alpha-3 code.

**Parameters:**
- `iso3code` (str): Three-letter country code (e.g., "USA", "FRA", "GBR")

**Returns:**
- `Optional[Country]`: Country data as a dictionary, or `None` if not found

**Raises:**
- `ValidationError`: If iso3code is not a valid 3-letter alphabetic string

**Example:**
```python
country = client.countries.get_by_iso3("USA")
```

---

#### `get_by_numeric_code(numeric_code: str) -> Optional[Country]`

Get a country by its ISO 3166-1 numeric code.

**Parameters:**
- `numeric_code` (str): Three-digit numeric code (e.g., "840", "250", "826")

**Returns:**
- `Optional[Country]`: Country data as a dictionary, or `None` if not found

**Raises:**
- `ValidationError`: If numeric_code is not a valid 3-digit string

**Example:**
```python
country = client.countries.get_by_numeric_code("840")
```

---

#### `get_all(limit: Optional[int] = None) -> List[Country]`

Get all countries.

**Parameters:**
- `limit` (Optional[int]): Maximum number of results to return. If `None`, returns all countries.

**Returns:**
- `List[Country]`: List of country dictionaries

**Raises:**
- `ValueError`: If limit is not a positive integer

**Example:**
```python
# Get all countries
all_countries = client.countries.get_all()

# Get first 10 countries
first_10 = client.countries.get_all(limit=10)
```

---

#### `get_by_region(region_id: str) -> List[Country]`

Get countries by World Bank region ID.

**Parameters:**
- `region_id` (str): Region ID (e.g., "NAC", "ECS", "SSF")

**Returns:**
- `List[Country]`: List of country dictionaries in the specified region

**Example:**
```python
# Get all countries in North America
north_america = client.countries.get_by_region("NAC")
```

**Common Region IDs:**
- `NAC`: North America
- `ECS`: Europe and Central Asia
- `SSF`: Sub-Saharan Africa
- `MEA`: Middle East and North Africa
- `EAS`: East Asia and Pacific
- `SAS`: South Asia
- `LCN`: Latin America and Caribbean

---

#### `get_by_income_level(income_level_id: str) -> List[Country]`

Get countries by World Bank income level.

**Parameters:**
- `income_level_id` (str): Income level ID (e.g., "OEC", "HIC", "LIC")

**Returns:**
- `List[Country]`: List of country dictionaries with the specified income level

**Example:**
```python
# Get high-income OECD countries
high_income = client.countries.get_by_income_level("OEC")
```

**Common Income Level IDs:**
- `OEC`: High income: OECD
- `HIC`: High income: nonOECD
- `UMC`: Upper middle income
- `LMC`: Lower middle income
- `LIC`: Low income

---

#### `get_un_members() -> List[Country]`

Get all UN member countries.

**Returns:**
- `List[Country]`: List of UN member country dictionaries

**Example:**
```python
un_members = client.countries.get_un_members()
print(f"Total UN members: {len(un_members)}")
```

---

#### `get_independent() -> List[Country]`

Get all independent countries.

**Returns:**
- `List[Country]`: List of independent country dictionaries

**Example:**
```python
independent = client.countries.get_independent()
```

---

#### `get_by_continent(continent: str) -> List[Country]`

Get countries by continent.

**Parameters:**
- `continent` (str): Continent name (e.g., "North America", "Europe", "Asia")

**Returns:**
- `List[Country]`: List of country dictionaries on the specified continent

**Example:**
```python
# Get all European countries
europe = client.countries.get_by_continent("Europe")
```

---

#### `get_by_currency(currency_code: str) -> List[Country]`

Get countries that use a specific currency.

**Parameters:**
- `currency_code` (str): Currency code (e.g., "USD", "EUR", "GBP")

**Returns:**
- `List[Country]`: List of country dictionaries using the specified currency

**Example:**
```python
# Get all countries using the Euro
euro_countries = client.countries.get_by_currency("EUR")
```

---

#### `get_by_language(language_code: str) -> List[Country]`

Get countries where a specific language is spoken.

**Parameters:**
- `language_code` (str): Language code (e.g., "eng", "fra", "spa")

**Returns:**
- `List[Country]`: List of country dictionaries where the language is spoken

**Example:**
```python
# Get all countries where English is spoken
english_countries = client.countries.get_by_language("eng")
```

---

#### `count() -> int`

Get the total number of countries.

**Returns:**
- `int`: Total count of countries

**Example:**
```python
total = client.countries.count()
print(f"Total countries: {total}")
```

---

## IntblocksClient

Client for querying international blocks data.

### Methods

#### `get_by_id(block_id: str) -> Optional[Intblock]`

Get an international block by its ID.

**Parameters:**
- `block_id` (str): Block identifier (e.g., "EU", "UN", "NATO")

**Returns:**
- `Optional[Intblock]`: Block data as a dictionary, or `None` if not found

**Example:**
```python
block = client.intblocks.get_by_id("EU")
if block:
    print(block["name"])  # "European Union"
```

---

#### `get_all(limit: Optional[int] = None) -> List[Intblock]`

Get all international blocks.

**Parameters:**
- `limit` (Optional[int]): Maximum number of results to return. If `None`, returns all blocks.

**Returns:**
- `List[Intblock]`: List of block dictionaries

**Raises:**
- `ValueError`: If limit is not a positive integer

**Example:**
```python
# Get all blocks
all_blocks = client.intblocks.get_all()

# Get first 5 blocks
first_5 = client.intblocks.get_all(limit=5)
```

---

#### `get_by_blocktype(blocktype: str) -> List[Intblock]`

Get blocks by type.

**Parameters:**
- `blocktype` (str): Block type (e.g., "economic", "political", "military")

**Returns:**
- `List[Intblock]`: List of block dictionaries of the specified type

**Example:**
```python
# Get all economic blocks
economic_blocks = client.intblocks.get_by_blocktype("economic")
```

**Common Block Types:**
- `economic`: Economic organizations
- `political`: Political organizations
- `military`: Military alliances
- `cultural`: Cultural organizations
- `environmental`: Environmental organizations

---

#### `get_by_status(status: str) -> List[Intblock]`

Get blocks by status.

**Parameters:**
- `status` (str): Status (e.g., "formal", "informal", "de-facto")

**Returns:**
- `List[Intblock]`: List of block dictionaries with the specified status

**Example:**
```python
# Get all formal organizations
formal_blocks = client.intblocks.get_by_status("formal")
```

---

#### `get_by_geographic_scope(scope: str) -> List[Intblock]`

Get blocks by geographic scope.

**Parameters:**
- `scope` (str): Geographic scope (e.g., "global", "regional", "sub-regional")

**Returns:**
- `List[Intblock]`: List of block dictionaries with the specified geographic scope

**Example:**
```python
# Get all global organizations
global_blocks = client.intblocks.get_by_geographic_scope("global")
```

---

#### `get_by_member(country_code: str) -> List[Intblock]`

Get blocks that include a specific country as a member.

**Parameters:**
- `country_code` (str): Two-letter country code (e.g., "US", "FR", "DE")

**Returns:**
- `List[Intblock]`: List of block dictionaries that include the specified country

**Example:**
```python
# Get all blocks that include the United States
us_blocks = client.intblocks.get_by_member("US")
```

---

#### `get_by_acronym(acronym: str) -> List[Intblock]`

Get blocks by acronym.

**Parameters:**
- `acronym` (str): Acronym (e.g., "EU", "UN", "NATO")

**Returns:**
- `List[Intblock]`: List of block dictionaries with the specified acronym

**Example:**
```python
# Find block by acronym
eu_block = client.intblocks.get_by_acronym("EU")
```

---

#### `get_by_tag(tag: str) -> List[Intblock]`

Get blocks by tag.

**Parameters:**
- `tag` (str): Tag keyword

**Returns:**
- `List[Intblock]`: List of block dictionaries with the specified tag

**Example:**
```python
# Get blocks tagged with "trade"
trade_blocks = client.intblocks.get_by_tag("trade")
```

---

#### `get_by_topic(topic_key: str) -> List[Intblock]`

Get blocks by topic key.

**Parameters:**
- `topic_key` (str): Topic key (e.g., "economy", "political", "trade")

**Returns:**
- `List[Intblock]`: List of block dictionaries with the specified topic

**Example:**
```python
# Get blocks related to economy
economy_blocks = client.intblocks.get_by_topic("economy")
```

---

#### `get_by_founded_year(year: int) -> List[Intblock]`

Get blocks founded in a specific year.

**Parameters:**
- `year` (int): Foundation year (e.g., 1993, 1945)

**Returns:**
- `List[Intblock]`: List of block dictionaries founded in the specified year

**Raises:**
- `ValidationError`: If year is not a valid integer in reasonable range (1000-9999)

**Example:**
```python
# Get blocks founded in 1993
blocks_1993 = client.intblocks.get_by_founded_year(1993)
```

---

#### `count() -> int`

Get the total number of international blocks.

**Returns:**
- `int`: Total count of blocks

**Example:**
```python
total = client.intblocks.count()
print(f"Total blocks: {total}")
```

---

## SearchClient

Client for searching countries and international blocks.

### Methods

#### `fuzzy(query: str, limit: int = 10, search_countries: bool = True, search_intblocks: bool = True) -> List[SearchResult]`

Perform fuzzy search across countries and international blocks.

This function searches across:
- Country names (in any language via native_names)
- Country codes (ISO 3166-1 alpha-2, alpha-3, numeric)
- International block names
- Block names in other languages (`other_names`)
- Block acronyms (in any language)
- Block IDs
- Block tags

**Parameters:**
- `query` (str): Search query string
- `limit` (int): Maximum number of results to return (default: 10)
- `search_countries` (bool): Whether to search countries (default: True)
- `search_intblocks` (bool): Whether to search international blocks (default: True)

**Returns:**
- `List[SearchResult]`: List of matching records with a 'type' field indicating 'country' or 'intblock'

**Raises:**
- `ValidationError`: If query is empty or limit is invalid

**Example:**
```python
# Search across both countries and blocks
results = client.search.fuzzy("United States")

# Search only countries
results = client.search.fuzzy("United", search_intblocks=False)

# Search only blocks
results = client.search.fuzzy("EU", search_countries=False)

# Multi-language search
results = client.search.fuzzy("Европа")  # Russian
results = client.search.fuzzy("欧盟")    # Chinese
```

**Search Behavior:**
- Exact matches (codes, IDs) are prioritized
- Partial matches are supported (case-insensitive)
- Results are sorted by relevance (exact matches first, then by name length)
- Duplicates are automatically removed

---

#### `search_countries(query: str, limit: int = 10) -> List[SearchResult]`

Search only countries.

**Parameters:**
- `query` (str): Search query string
- `limit` (int): Maximum number of results to return (default: 10)

**Returns:**
- `List[SearchResult]`: List of matching country dictionaries

**Example:**
```python
# Search only countries
countries = client.search.search_countries("United")
```

---

#### `search_intblocks(query: str, limit: int = 10) -> List[SearchResult]`

Search only international blocks.

**Parameters:**
- `query` (str): Search query string
- `limit` (int): Maximum number of results to return (default: 10)

**Returns:**
- `List[SearchResult]`: List of matching block dictionaries

**Example:**
```python
# Search only blocks
blocks = client.search.search_intblocks("EU")
```

---

## Downloader Functions

Functions for downloading and managing the database.

### `download_database(version: Optional[str] = None, force: bool = False, show_progress: bool = True, cache_dir: Optional[Path] = None) -> Path`

Download the database from GitHub releases.

**Parameters:**
- `version` (Optional[str]): Version string (e.g., "v1.0.0"). If `None`, downloads the latest version.
- `force` (bool): Force re-download even if already cached (default: False)
- `show_progress` (bool): Show download progress bar (default: True, requires `tqdm`)
- `cache_dir` (Optional[Path]): Custom cache directory. If `None`, uses default cache location.

**Returns:**
- `Path`: Path to the downloaded database file

**Raises:**
- `DownloadError`: If download fails
- `VersionError`: If specified version not found

**Example:**
```python
from internacia import download_database

# Download latest version
db_path = download_database()

# Download specific version
db_path = download_database(version="v1.0.0")

# Force re-download
db_path = download_database(force=True)
```

---

### `get_latest_version() -> str`

Fetch the latest release version from GitHub.

**Returns:**
- `str`: Latest version string (e.g., "v1.0.0")

**Raises:**
- `DownloadError`: If unable to fetch version information
- `VersionError`: If no releases found

**Example:**
```python
from internacia import get_latest_version

latest = get_latest_version()
print(f"Latest version: {latest}")
```

---

### `check_for_updates() -> dict`

Check if a newer database version is available.

**Returns:**
- `dict`: Dictionary with keys:
  - `has_update` (bool): Whether an update is available
  - `current_version` (Optional[str]): Current cached version, if any
  - `latest_version` (str): Latest available version

**Raises:**
- `DownloadError`: If unable to check for updates

**Example:**
```python
from internacia import check_for_updates

update_info = check_for_updates()
if update_info["has_update"]:
    print(f"Update available: {update_info['latest_version']}")
```

---

### `list_releases() -> list`

List all available releases and their database file status.

**Returns:**
- `list`: List of dictionaries with release information:
  - `version` (str): Release version
  - `published_at` (str): Publication date
  - `has_database` (bool): Whether the release includes a database file
  - `database_size` (Optional[int]): Database file size in bytes, if available

**Raises:**
- `DownloadError`: If unable to fetch releases

**Example:**
```python
from internacia import list_releases

releases = list_releases()
for release in releases:
    if release["has_database"]:
        print(f"{release['version']}: {release['database_size']} bytes")
```

---

### `get_cache_dir() -> Path`

Get the cache directory for downloaded databases.

**Returns:**
- `Path`: Path to cache directory

**Example:**
```python
from internacia import get_cache_dir

cache_dir = get_cache_dir()
print(f"Cache directory: {cache_dir}")
```

---

### `get_cached_database_path(version: Optional[str] = None) -> Path`

Get the path to the cached database file.

**Parameters:**
- `version` (Optional[str]): Optional version string. If `None`, returns path to latest cache.

**Returns:**
- `Path`: Path to cached database file

**Example:**
```python
from internacia import get_cached_database_path

# Get latest cached database path
latest_path = get_cached_database_path()

# Get specific version path
version_path = get_cached_database_path(version="v1.0.0")
```

---

## Data Models

### Country

Country data structure.

**Fields:**
- `code` (str): ISO 3166-1 alpha-2 code (e.g., "US")
- `name` (str): Common name
- `iso3code` (str): ISO 3166-1 alpha-3 code
- `numeric_code` (str): ISO 3166-1 numeric code
- `official_name` (Optional[str]): Official full name
- `capital_city` (Optional[CapitalCity]): Capital city information
- `region` (Optional[Region]): World Bank region information
- `incomeLevel` (Optional[IncomeLevel]): World Bank income level information
- `languages` (List[Language]): List of languages spoken
- `currencies` (List[Currency]): List of currencies used
- `un_member` (bool): Whether the country is a UN member
- `independent` (bool): Whether the country is independent
- `continents` (List[str]): List of continent names
- `borders` (List[str]): List of bordering country codes
- `native_names` (Dict[str, NativeName]): Map of language code to native names

**Example:**
```python
country = client.countries.get_by_code("US")
print(country["name"])  # "United States"
print(country["capital_city"]["name"])  # "Washington"
```

---

### Intblock

International block data structure.

**Fields:**
- `id` (str): Unique identifier
- `name` (str): Name of the block
- `blocktype` (List[str]): List of types (e.g., ["economic", "political"])
- `status` (str): Status ("formal", "informal", "de-facto")
- `other_names` (Optional[List[OtherName]]): Names in other languages
- `acronyms` (List[Acronym]): List of acronyms in different languages
- `includes` (List[Member]): List of member countries
- `founded` (Optional[str]): Foundation year/date
- `geographic_scope` (Optional[str]): Scope ("global", "regional", "sub-regional")
- `scope_category` (Optional[str]): Scope category. This is an open string: new values can appear in any MINOR data release, so do not treat it as a closed enum.
- `tags` (List[str]): List of classification tags
- `topics` (List[Topic]): List of topics

**Example:**
```python
block = client.intblocks.get_by_id("EU")
print(block["name"])  # "European Union"
print(block["blocktype"])  # ["economic", "political"]
```

---

### SearchResult

Search result with type indicator.

**Fields:**
- `type` (str): Either "country" or "intblock"
- All fields from `Country` or `Intblock` depending on type

**Example:**
```python
results = client.search.fuzzy("United States")
for result in results:
    if result["type"] == "country":
        print(f"Country: {result['name']}")
    elif result["type"] == "intblock":
        print(f"Block: {result['name']}")
```

---

### Supporting Types

#### CapitalCity
- `name` (str): Capital city name
- `lng` (float): Longitude
- `lat` (float): Latitude

#### Region
- `id` (str): Region ID
- `value` (str): Region name

#### IncomeLevel
- `id` (str): Income level ID
- `value` (str): Income level name

#### Language
- `code` (str): Language code
- `name` (str): Language name
- `official` (bool): Whether it's an official language

#### Currency
- `code` (str): Currency code
- `name` (str): Currency name
- `symbol` (str): Currency symbol

#### NativeName
- `official` (str): Official native name
- `common` (str): Common native name

#### OtherName
- `id` (str): Language code
- `name` (str): Name in that language

#### Acronym
- `lang` (str): Language code
- `value` (str): Acronym value

#### Topic
- `key` (str): Topic key
- `name` (str): Topic name

#### Member
- `id` (str): Country code
- `name` (str): Country name
- `type` (Optional[str]): Member type
- `status` (Optional[str]): Member status

---

## Exceptions

### InternaciaError

Base exception for all internacia SDK errors.

**Inherits from:** `Exception`

---

### DatabaseError

Database-related errors (connection failures, query errors, etc.).

**Inherits from:** `InternaciaError`

**Example:**
```python
try:
    country = client.countries.get_by_code("US")
except DatabaseError as e:
    print(f"Database error: {e}")
```

---

### NotFoundError

Resource not found errors (e.g., country code doesn't exist).

**Inherits from:** `InternaciaError`

**Example:**
```python
try:
    country = client.countries.get_by_code("XX")
except NotFoundError as e:
    print(f"Not found: {e}")
```

---

### ValidationError

Input validation errors (e.g., empty query string, invalid code format).

**Inherits from:** `InternaciaError`

**Example:**
```python
try:
    country = client.countries.get_by_code("123")  # Invalid format
except ValidationError as e:
    print(f"Validation error: {e}")
```

---

### DownloadError

Database download-related errors.

**Inherits from:** `InternaciaError`

**Example:**
```python
try:
    download_database()
except DownloadError as e:
    print(f"Download error: {e}")
```

---

### VersionError

Version-related errors (e.g., version not found).

**Inherits from:** `InternaciaError`

**Example:**
```python
try:
    download_database(version="v999.0.0")  # Non-existent version
except VersionError as e:
    print(f"Version error: {e}")
```

---

## Return Types

All functions return pure Python types:
- **Dictionaries**: All data structures are returned as Python dictionaries (TypedDict for type hints)
- **Lists**: Collections are returned as Python lists
- **Integers**: Count methods return Python integers
- **None**: Optional return values use Python `None`. Any field of a returned record can be `None`, including nested lists such as `currencies` and `languages`; iterate with `country.get("currencies") or []`.
- **Path**: Path-related functions return `pathlib.Path` objects

**No numpy arrays or pandas DataFrames are returned** - all data is converted to standard Python types before being returned to users.

