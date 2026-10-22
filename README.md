# Internacia Python SDK

A Python SDK for accessing [internacia-db](https://github.com/datenoio/internacia-db) data with support for countries, international blocks, and fuzzy search across multiple languages.

## Features

- 🌍 **Countries Data**: Access comprehensive country information including codes, names, currencies, languages, and more
- 🏛️ **International Blocks**: Query international organizations, alliances, and unions
- 🔍 **Fuzzy Search**: Multi-language search supporting partial matches across names, codes, acronyms, and names in other languages
- 🚀 **Thread-Safe**: Built on DuckDB with thread-safe connection handling
- 🌐 **Multi-Language**: Search works across all languages supported in the dataset
- ⚡ **Fast**: Leverages DuckDB for high-performance queries
- ✅ **Well-Tested**: Comprehensive test suite with 100% coverage of all public APIs

## Compatibility

| internacia (SDK) | internacia-db data | duckdb | Python |
|---|---|---|---|
| 0.4.x | 3.x (contract 3.x; tested against 3.1.0) | `>=1.5.4,<3` | `>=3.11` |
| 0.3.x | 3.x (tested against 3.0.0) | `>=1.5.4,<3` | `>=3.11` |
| 0.2.0 | 1.x–2.x; broken on 3.x | `>=0.9.0` | `>=3.8` (declared) |

## Installation

```bash
pip install internacia
```

For download progress bars, install with the `progress` extra:

```bash
pip install internacia[progress]
```

For the MCP server (`internacia-mcp`), install the `mcp` extra:

```bash
pip install internacia[mcp]
```

Or install from source:

```bash
git clone https://github.com/datenoio/internacia-python.git
cd internacia-python
pip install -e .
```

## Getting the database

The SDK reads an `internacia.duckdb` file from an
[internacia-db release](https://github.com/datenoio/internacia-db/releases). Download it once
(similar to NLTK's download mechanism):

```python
from internacia import InternaciaClient, download_database

download_database()                    # newest release with a supported contract
download_database(version="3.0.0")     # a specific release ("v3.0.0" also works)
download_database(force=True)          # re-download even if cached
download_database(show_progress=True)  # progress bar (pip install internacia[progress])

client = InternaciaClient()            # uses the newest cached release
```

- Files come from direct release download URLs, so downloading does not hit the GitHub API
  rate limit. The API is only used by `list_releases()`, or when the latest release has a
  newer contract major; set `GITHUB_TOKEN` to authenticate those calls.
- Each download is checked against the release's `SHA256SUMS`. Releases published before
  `SHA256SUMS` existed (v3.0.0) are downloaded with a warning.
- Releases are cached in `~/.internacia/<tag>/internacia.duckdb` (override with
  `INTERNACIA_CACHE_DIR`). The client picks the newest cached release by semantic version.

Pin a release with `InternaciaClient(data_version="3.0.0")` or `INTERNACIA_DATA_VERSION`; the
same variable is the default version for `download_database()`. To use any other file (for
example a local `python scripts/builder.py build` in internacia-db), pass `db_path=` or set
`INTERNACIA_DB_PATH`.

```python
from internacia import check_for_updates, cached_versions, get_latest_version

update = check_for_updates()   # compares the newest cached release with the newest release
if update["has_update"]:
    download_database(update["latest_version"])

print(get_latest_version(), cached_versions())
```

### Version and contract

```python
meta = client.meta()
meta["version"]            # "3.0.0"
meta["contract_version"]   # "3.0"
meta["datasets"]["countries"]  # {"row_count": 256, "schema_hash": "..."}
```

internacia-db versions its schema as a data contract (`contract_version` = `MAJOR.MINOR`). This
SDK release supports contract **3.x** and was tested against **3.0**:

- A different MAJOR raises `ContractError` when the client is created.
- A newer MINOR (new tables, columns or enum values) is accepted with a logged warning.
- `InternaciaClient(check_contract=False)` skips the check.
- Enum-like fields (`status`, `scope_category`, `geographic_scope`, …) are open strings: new
  values can appear in any MINOR release.


### Memberships, block types and retired IDs

```python
with InternaciaClient() as client:   # closes the connection on exit
    # Current membership edges (no former members, no left date, block not dissolved)
    nato = client.memberships.get_by_intblock("NATO")
    full = [m["country_code"] for m in nato if m["status"] in ("member", "founding_member")]
    history = client.memberships.get_by_country("US", current_only=False)
    client.memberships.is_member("US", "NAFTA")             # False (left in 2020)

    client.intblocks.get_by_member("US", current_only=True)  # blocks, current only
    client.blocktypes.get_all()                              # the blocktype taxonomy

    client.intblocks.resolve_id("USAN")    # {"id": "UNASUR", "status": "merged", ...}
    client.countries.resolve_code("KV")    # {"id": "XK", "status": "renamed", ...}
```

`resolve_id` returns `status` `current`, an alias reason (`renamed`, `merged`, `retired`) with
the replacement `id` (None when retired), or `unknown`. `disambiguated` is set when the id is
current but used to name another entity. Alias resolution needs an internacia-db release that
ships the alias tables inside `internacia.duckdb` (after 3.0.0); with 3.0.0 only `current` and
`unknown` are reported.

### Derived catalogs

Currencies, languages, time zones and regions come from the canonical views of the data
contract (or the same SQL on databases built before the views existed). Countries with no
currencies, languages or time zones simply have no rows.

```python
client.countries.get_currencies()               # [{"code", "name", "symbol", "country_count"}]
client.countries.get_currency("EUR")
client.countries.get_country_currencies("CH")   # [{"code": "CHF", ...}]
client.countries.get_languages(); client.countries.get_country_languages("BE")
client.countries.get_timezones(); client.countries.get_country_timezones("RU")
client.countries.get_by_timezone("Europe/Paris")
client.countries.get_regions(); client.countries.get_region("ECS")
```


### LLM tools

`internacia.tools` turns the SDK into function-calling tools. Every public query method is a
tool (`countries_get_by_code`, `memberships_get_by_intblock`, …) whose schema is generated from
its signature and docstring, plus two composite tools, `country_lookup` and `intblock_lookup`.
Passing a client fills `enum` lists (regions, statuses, block types, scope categories) from the
connected data version.

```python
from internacia import InternaciaClient
from internacia.tools import call_tool, openai_tools, tool_schemas

client = InternaciaClient()
tools = openai_tools(client)        # OpenAI "tools" format; tool_schemas() for plain JSON Schema

# After the model returns a tool call:
result = call_tool(client, "intblock_lookup", '{"member_country": "FR", "scope_category": "igo"}')
```

`call_tool` accepts the arguments as a dict or as the JSON string LLM APIs return, and returns
JSON-serializable data.

### MCP server

The same tools are available to MCP clients (Claude Desktop, Cursor, …) through a stdio server:

```bash
pip install internacia[mcp]
internacia-mcp
```

```json
{"mcpServers": {"internacia": {"command": "internacia-mcp"}}}
```

The server finds the database like the client does (`INTERNACIA_DB_PATH`,
`INTERNACIA_DATA_VERSION` or the download cache); set them in the client's `env` block.
`internacia.mcp_server.build_server(client)` returns the server for embedding.

## Quick Start

```python
from internacia import InternaciaClient

# Initialize the client
client = InternaciaClient()

# Get a country by code
country = client.countries.get_by_code("US")
print(country["name"])  # "United States"

# Search for countries or blocks
results = client.search.fuzzy("United States")
for result in results:
    print(f"{result['type']}: {result['name']}")

# Get an international block
block = client.intblocks.get_by_id("EU")
print(block["name"])  # "European Union"
```

## Usage

### Countries

#### Get Country by Code

```python
# By ISO 3166-1 alpha-2 code
country = client.countries.get_by_code("US")

# By ISO 3166-1 alpha-3 code
country = client.countries.get_by_iso3("USA")

# By numeric code
country = client.countries.get_by_numeric_code("840")
```

#### Query Countries

```python
# Get all countries
all_countries = client.countries.get_all()

# Get UN members
un_members = client.countries.get_un_members()

# Get independent countries
independent = client.countries.get_independent()

# Get countries by region
countries = client.countries.get_by_region("NAC")  # North America

# Get countries by income level
countries = client.countries.get_by_income_level("OEC")  # High income: OECD

# Get countries by continent
countries = client.countries.get_by_continent("Europe")

# Get countries by currency
countries = client.countries.get_by_currency("EUR")

# Get countries by language
countries = client.countries.get_by_language("eng")

# Get total count
count = client.countries.count()
```

### International Blocks

#### Get Block by ID

```python
block = client.intblocks.get_by_id("EU")
```

#### Query Blocks

```python
# Get all blocks
all_blocks = client.intblocks.get_all()

# Get blocks by type
blocks = client.intblocks.get_by_blocktype("economic")

# Get blocks by status
blocks = client.intblocks.get_by_status("formal")

# Get blocks by geographic scope
blocks = client.intblocks.get_by_geographic_scope("regional")

# Get blocks containing a specific country
blocks = client.intblocks.get_by_member("US")

# Get blocks by acronym
blocks = client.intblocks.get_by_acronym("EU")

# Get blocks by tag
blocks = client.intblocks.get_by_tag("trade")

# Get blocks by topic
blocks = client.intblocks.get_by_topic("economy")

# Get blocks founded in a specific year
blocks = client.intblocks.get_by_founded_year(1993)

# Get total count
count = client.intblocks.count()
```

### Search

#### Fuzzy Search

The fuzzy search function searches across countries and international blocks, supporting:

- Country names (in any language via native_names)
- Country codes (ISO 3166-1 alpha-2, alpha-3, numeric)
- International block names
- Block names in other languages (`other_names`)
- Block acronyms (in any language)
- Block IDs
- Block tags

```python
# Search across both countries and blocks
results = client.search.fuzzy("United States")

# Search only countries
countries = client.search.search_countries("United")

# Search only blocks
blocks = client.search.search_intblocks("EU")

# Search with custom limit
results = client.search.fuzzy("Europe", limit=5)

# Control search scope
results = client.search.fuzzy("EU", search_countries=False, search_intblocks=True)

# Multi-language search
results = client.search.fuzzy("Европа")  # Russian
results = client.search.fuzzy("欧盟")    # Chinese
results = client.search.fuzzy("UE")      # French acronym
```

The `fuzzy()` method supports the following parameters:
- `query`: Search query string (required)
- `limit`: Maximum number of results to return (default: 10)
- `search_countries`: Whether to search countries (default: True)
- `search_intblocks`: Whether to search international blocks (default: True)

Results are ranked: exact codes and block ids first, then names (or codes and ids) that start
with the query, then other matches; ties go to shorter names. Each table is searched with one
query. `%` and `_` in the query match literally.

### Custom Database Path

If your database is in a different location:

```python
from pathlib import Path

client = InternaciaClient(
    db_path=Path("/path/to/internacia.duckdb")
)
```

### Configuration

The SDK supports multiple ways to configure database paths and logging:

#### Environment Variables

```bash
# Set custom database path
export INTERNACIA_DB_PATH="/path/to/internacia.duckdb"

# Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
export INTERNACIA_LOG_LEVEL="DEBUG"

# Set custom cache directory for downloaded databases
export INTERNACIA_CACHE_DIR="/path/to/cache"

# Pin a cached release (also the default for download_database())
export INTERNACIA_DATA_VERSION="3.0.0"

# Authenticate GitHub API calls (list_releases)
export GITHUB_TOKEN="..."
```

The SDK will automatically use these environment variables if set. Priority order for database path resolution:
1. Explicit `db_path` parameter
2. `INTERNACIA_DB_PATH` environment variable
3. The cached release pinned by `data_version` / `INTERNACIA_DATA_VERSION`
4. The newest cached release with a supported contract major

#### Logging

The SDK logs through the standard `logging` module under the `internacia` logger and never
attaches handlers of its own (the package logger has a `NullHandler`). Configure output in
your application:

```python
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("internacia").setLevel(logging.DEBUG)  # queries and row counts
```

`INTERNACIA_LOG_LEVEL` (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) sets the level of the
`internacia` logger when a client is created.

### Type Hints

The SDK provides comprehensive type hints using TypedDict models for better IDE support and type checking:

```python
from internacia import InternaciaClient, Country, Intblock, SearchResult

client = InternaciaClient()

# All methods return properly typed dictionaries
country: Country = client.countries.get_by_code("US")
block: Intblock = client.intblocks.get_by_id("EU")
results: list[SearchResult] = client.search.fuzzy("United States")
```

Available types:
- `Country`: Country data structure
- `Intblock`: International block data structure
- `SearchResult`: Search result with type indicator
- Supporting types: `CapitalCity`, `Region`, `IncomeLevel`, `Language`, `Currency`, `NativeName`, `OtherName`, `Acronym`, `Topic`, `Member`

### Error Handling

The SDK provides a custom exception hierarchy for better error handling:

```python
from internacia import InternaciaClient
from internacia.exceptions import (
    InternaciaError,
    DatabaseError,
    NotFoundError,
    ValidationError,
    DownloadError,
    VersionError,
)

client = InternaciaClient()

try:
    country = client.countries.get_by_code("XX")  # Invalid code
except ValidationError as e:
    print(f"Invalid input: {e}")
except NotFoundError as e:
    print(f"Not found: {e}")
except DatabaseError as e:
    print(f"Database error: {e}")
```

Exception types:
- `InternaciaError`: Base exception for all SDK errors
- `DatabaseError`: Database connection or query errors
- `NotFoundError`: Resource not found (e.g., country code doesn't exist)
- `ValidationError`: Input validation errors (e.g., empty query string)
- `DownloadError`: Database download or checksum verification failures
- `VersionError`: Version-related errors
- `ContractError` (a `VersionError`): the database's data contract major is not supported

## Data Structure

### Country Fields

- `code`: ISO 3166-1 alpha-2 code (e.g., "US")
- `name`: Common name
- `iso3code`: ISO 3166-1 alpha-3 code
- `numeric_code`: ISO 3166-1 numeric code
- `official_name`: Official full name
- `capital_city`: `{name, lng, lat}`
- `region`: World Bank region `{id, value}`
- `incomeLevel`: World Bank income level `{id, value}`
- `languages`: List of `{code, name, official}`
- `currencies`: List of `{code, name, symbol}`
- `un_member`: Boolean
- `independent`: Boolean
- `continents`: List of continent names
- `borders`: List of bordering country codes
- `native_names`: Map of language code -> `{official, common}`
- And more...

### International Block Fields

- `id`: Unique identifier
- `name`: Name of the block
- `blocktype`: List of types (e.g., ["economic", "political"])
- `status`: Status ("formal", "informal", "de-facto")
- `other_names`: List of `{id, name}`, where `id` is the language code
- `acronyms`: List of `{lang, value}`
- `includes`: List of member countries `{id, name, type, status, ...}`
- `founded`: Foundation year/date
- `geographic_scope`: Scope ("global", "regional", "sub-regional")
- `scope_category`: Scope category (an open string; new values can appear in any data release)
- `tags`: List of classification tags
- `topics`: List of `{key, name}`
- And more...

## Thread Safety

The SDK is designed to be thread-safe. Each query uses its own read-only DuckDB connection, which is automatically closed after use. This allows safe concurrent access from multiple threads.

```python
import threading
from internacia import InternaciaClient

client = InternaciaClient()

def query_country(code):
    country = client.countries.get_by_code(code)
    print(f"{code}: {country['name']}")

# Safe to use from multiple threads
threads = []
for code in ["US", "FR", "DE", "GB"]:
    t = threading.Thread(target=query_country, args=(code,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

## Examples

See the `examples/` directory for more detailed usage examples:

- `basic_usage.py`: Basic operations
- `search_examples.py`: Search functionality
- `advanced_queries.py`: Complex queries
- `multi_language.py`: Multi-language search examples

## Development

### Setup

```bash
git clone https://github.com/datenoio/internacia-python.git
cd internacia-python
pip install -e ".[dev]"
```

### Running Tests

The suite has three parts:

- **Unit tests** (`tests/test_*.py`) mock the database and cover validation, error paths and the downloader.
- **Integration tests** (`tests/integration/`) run every public method and every `examples/*.py` script against a real internacia-db release DuckDB file. They are skipped unless `INTERNACIA_TEST_DB_PATH` is set, and they fail in CI if it is missing.
- **Contract tests** (`tests/contract/`) are the portable subset that internacia-db runs against every fresh build before a release (`INTERNACIA_CONTRACT_DB_PATH`, falling back to `INTERNACIA_TEST_DB_PATH` here). They check `meta()` and the contract, every public method on stable facts, plain Python result types, and that unknown enum values are accepted.

```bash
# Unit tests only
pytest

# Download the pinned release database (version and SHA-256 are in tests/internacia-db.json)
python scripts/fetch_test_db.py --version 3.0.0 \
  --sha256 02c33d6822432ef60bce19b81e33b180221f6d6504c3e163f0e14f866254e01d \
  --output .test-data/internacia.duckdb

# Unit and integration tests
INTERNACIA_TEST_DB_PATH=.test-data/internacia.duckdb INTERNACIA_TEST_DB_VERSION=3.0.0 pytest

# With coverage report
pytest --cov=internacia --cov-report=html
```

New internacia-db releases are picked up by `.github/workflows/data-bump.yml`: daily, and when
internacia-db announces a release, it runs `scripts/data_bump.py`, which moves
`tests/internacia-db.json` (and `TESTED_CONTRACT` for a new contract minor) to the new release
and opens a pull request. With the same contract major the pull request merges itself once CI
passes; a new major waits for SDK changes. It needs the internacia-bot GitHub App, "Allow
auto-merge", and branch protection on `main` that requires the CI checks.

CI runs the full suite on Python 3.11, 3.12 and 3.13 with both the minimum supported duckdb (1.5.4) and the newest allowed one.

### Code Formatting

```bash
black internacia/ tests/ examples/ scripts/
ruff check internacia/ tests/ examples/ scripts/
mypy internacia/
```

### Pre-commit Hooks

The project includes pre-commit hooks for automated code quality checks:

```bash
# Install pre-commit hooks
pre-commit install

# Run hooks manually on all files
pre-commit run --all-files
```

The hooks automatically check for:
- Code formatting (black)
- Linting (ruff)
- Type checking (mypy)
- Test execution (pytest)
- Trailing whitespace and other code quality issues

### Alternative Implementation Approaches for Database Updates

While the current SDK uses a manual update process, here are several alternative approaches that could be implemented to automate database updates:

#### 1. Version Metadata Checking
**Approach**: Store version/timestamp metadata in the database and provide SDK methods to check for updates.

**Implementation**:
- Add a `metadata` table to the database with version, build date, and checksum
- Provide `client.get_database_version()` and `client.check_for_updates()` methods
- Compare local version with remote version (from API or file)

**Pros**: Simple, lightweight, no external dependencies
**Cons**: Requires coordination with internacia-db to maintain version info
**Complexity**: Low

#### 2. CLI Update Command
**Approach**: Create a CLI tool (e.g., `internacia update`) that automates the rebuild process.

**Implementation**:
- Add a CLI entry point using `click` or `argparse`
- Command navigates to internacia-db, pulls updates, and rebuilds
- Can be run manually or via cron/scheduled tasks

**Pros**: User-friendly, automates the manual process
**Cons**: Requires internacia-db to be accessible locally
**Complexity**: Medium

#### 3. Auto-Download from Releases
**Approach**: Automatically download pre-built database files from GitHub releases.

**Implementation**:
- Publish database files as GitHub release assets in internacia-db
- SDK checks for new releases and downloads the database file
- Cache downloaded files locally

**Pros**: No build step required, works for all users
**Cons**: Requires release management, larger repository size
**Complexity**: Medium-High

#### 4. Database Version API
**Approach**: Check against an API endpoint for the latest database version.

**Implementation**:
- Create a simple API endpoint (or use internacia-api) that returns latest version info
- SDK queries API on initialization or via a method call
- Compare versions and prompt user to update

**Pros**: Centralized version management, can provide update notifications
**Cons**: Requires API infrastructure, network dependency
**Complexity**: Medium-High

#### 5. Watch Mode / File Monitoring
**Approach**: Monitor the database file for changes and reload automatically.

**Implementation**:
- Use file system watchers (e.g., `watchdog` library) to detect database file changes
- Automatically reload database connections when file is updated
- Useful for development environments

**Pros**: Seamless updates during development
**Cons**: File watching overhead, primarily useful for development
**Complexity**: Medium

#### 6. Package Integration with Version Checking
**Approach**: Include database version checking in SDK initialization with warnings.

**Implementation**:
- Check database version on client initialization
- Compare against expected/known versions
- Log warnings if database is outdated
- Optionally provide update instructions in the warning

**Pros**: Proactive user notification, minimal implementation
**Cons**: Requires version metadata in database
**Complexity**: Low-Medium

**Recommendation**: Start with **Version Metadata Checking** (#1) combined with **Package Integration** (#6) for a lightweight solution that provides user feedback. For more advanced use cases, consider **CLI Update Command** (#2) or **Auto-Download from Releases** (#3).

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Related Projects

- [internacia-db](https://github.com/datenoio/internacia-db): The data repository
- [internacia-api](https://github.com/datenoio/internacia-api): REST API for internacia-db

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes.

