# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - Unreleased

### Added
- `InternaciaClient.meta()`: version, `contract_version`, build identity and per-dataset row
  counts and schema hashes from `_meta`.
- Data contract check when the client is created: a different contract major raises the new
  `ContractError`, a newer minor logs a warning (`check_contract=False` skips it). This release
  supports contract 3.x and was tested against 3.0.
- `InternaciaClient(data_version=...)` and `INTERNACIA_DATA_VERSION` pin a cached release;
  `cached_versions()` lists cached releases newest first.
- `tests/contract/`: portable data-contract suite that internacia-db runs against fresh builds.
- `client.memberships`: current or all membership edges by block or country, and
  `is_member()`. "Current" follows the internacia-db `current_memberships` view.
- `client.intblocks.get_by_member(..., current_only=True)`.
- `client.blocktypes`: the blocktype taxonomy.
- `client.intblocks.resolve_id()` and `client.countries.resolve_code()` resolve retired,
  renamed and merged identifiers through the alias tables in `internacia.duckdb`.
- Derived catalogs on `client.countries`: currencies, languages, time zones and regions, from
  the canonical views (with the same SQL on databases without them).
- `InternaciaClient.close()` and context-manager support.
- `tests/contract` covers the new methods.
- `internacia.tools`: LLM function-calling schemas generated from the SDK's signatures and
  docstrings (OpenAI and plain JSON Schema formats), enum lists from the connected database, and
  `call_tool()` to execute tool calls. Replaces the hand-written `*_lookup.openai.json` files in
  internacia-db.

### Changed
- `download_database()` uses direct release download URLs (no GitHub API rate limit), resolves
  the latest release from the `/releases/latest` redirect, and verifies the file against the
  release's `SHA256SUMS` (releases without it, such as v3.0.0, download with a warning). The
  default is the newest release with a supported contract major.
- The cache is resolved by semantic version (`~/.internacia/<tag>/`), not by directory order.
- `check_for_updates()` compares the newest cached release with the latest release instead of
  always reporting an update; `list_releases()` sends `GITHUB_TOKEN` when set.
- One read-only DuckDB connection per client (a cursor per query) instead of one connection per
  query.
- The SDK no longer attaches logging handlers; `INTERNACIA_LOG_LEVEL` only sets the level.

### Removed
- The sibling `../internacia-db/data/datasets/internacia.duckdb` fallback and
  `scripts/update_database.sh`; use `INTERNACIA_DB_PATH` for local builds.
- `get_database_info()` (internal; release metadata came from the GitHub API).

## [0.3.0] - Unreleased

Supports internacia-db 3.x data. Tested against internacia-db 3.0.0.

### Packaging

- `requires-python>=3.11`; Python 3.8–3.10 are no longer supported (3.8 never worked).
- `pyproject.toml` is the only build configuration; `setup.py` and `requirements.txt` are removed. The version is read from `internacia/version.py`.
- Project URLs point to `github.com/datenoio`.
- Releases are published from a `v*` tag by `.github/workflows/release.yml` through PyPI Trusted Publishing.
- Removed the VS Code workspace file from the package directory and stopped tracking `dev/docs/`.

### Fixed

- Compatibility with internacia-db v3: every public method now works against the v3.0.0 DuckDB on duckdb 1.5.4 and 2.x.
  - Nested-list filters (`get_by_currency`, `get_by_language`, `get_by_member`, `get_by_acronym`, `get_by_topic` and search) use the version-portable `EXISTS (SELECT 1 FROM UNNEST(col) AS t(x) WHERE x.field = ?)` form.
  - Block search uses `other_names` instead of the `translations` column, which internacia-db removed in 1.6.0.
  - Multilingual country search uses `map_values(native_names)` and matches both `common` and `official` names. Previously it failed silently and returned nothing.
  - A failing search query now raises `DatabaseError` instead of being logged and skipped.
- Results are plain Python types (`list`, `dict`, `None`) and JSON-serializable. Rows come from `fetchall()` and `cursor.description`, not pandas.

### Changed

- `duckdb>=1.5.4,<3` (was `>=0.9.0`; 0.9.x cannot open the v3 file).
- Removed the `pandas` dependency.
- Model fields are typed `Optional`, because every internacia-db column is nullable. `scope_category` and other enum-like columns are open strings.
- `Intblock` gains `other_names` and `scope_category`; `Country` gains `other_names`; `Member` gains `joined`, `left`, `role` and `note`.

### Removed

- `Intblock.translations` and the `Translation` type. Use `other_names` and `OtherName`.

### Testing

- Integration tests (`tests/integration/`) run every public method and every example script against the internacia-db v3.0.0 release DuckDB, downloaded and SHA-256-verified by `scripts/fetch_test_db.py`.
- CI matrix: Python 3.11–3.13 × duckdb 1.5.4 and newest `<3`, plus macOS and Windows. The Python 3.8–3.10 jobs are removed.
- black, ruff and mypy pass; tool versions and the ruff rule set are pinned in `pyproject.toml` and `.pre-commit-config.yaml`.

## [0.2.0] - 2025-12-20

Initial release of Internacia Python SDK

### Added

- Initial release of Internacia Python SDK
- `InternaciaClient` main client class
- `CountriesClient` for querying country data
  - `get_by_code()`: Get country by ISO 3166-1 alpha-2 code
  - `get_by_iso3()`: Get country by ISO 3166-1 alpha-3 code
  - `get_by_numeric_code()`: Get country by numeric code
  - `get_all()`: Get all countries
  - `get_by_region()`: Get countries by World Bank region
  - `get_by_income_level()`: Get countries by income level
  - `get_un_members()`: Get UN member countries
  - `get_independent()`: Get independent countries
  - `get_by_continent()`: Get countries by continent
  - `get_by_currency()`: Get countries by currency
  - `get_by_language()`: Get countries by language
  - `count()`: Get total count of countries
- `IntblocksClient` for querying international blocks data
  - `get_by_id()`: Get block by ID
  - `get_all()`: Get all blocks
  - `get_by_blocktype()`: Get blocks by type
  - `get_by_status()`: Get blocks by status
  - `get_by_geographic_scope()`: Get blocks by geographic scope
  - `get_by_member()`: Get blocks containing a country
  - `get_by_acronym()`: Get blocks by acronym
  - `get_by_tag()`: Get blocks by tag
  - `get_by_topic()`: Get blocks by topic
  - `get_by_founded_year()`: Get blocks by foundation year
  - `count()`: Get total count of blocks
- `SearchClient` for fuzzy search functionality
  - `fuzzy()`: Multi-language fuzzy search across countries and blocks with configurable search scope
  - `search_countries()`: Search only countries
  - `search_intblocks()`: Search only blocks
- Database download functionality (similar to NLTK's download mechanism)
  - `download_database()`: Download pre-built database from GitHub releases
  - `get_latest_version()`: Get latest database version
  - `check_for_updates()`: Check if database updates are available
  - `get_cache_dir()`: Get cache directory path
  - `get_cached_database_path()`: Get cached database file path
  - Automatic caching in `~/.internacia/` directory
  - Support for versioned downloads and force re-download
  - Progress bar support (with optional `tqdm` dependency)
- Configuration management
  - `Config` class for centralized configuration
  - Environment variable support: `INTERNACIA_DB_PATH`, `INTERNACIA_LOG_LEVEL`, `INTERNACIA_CACHE_DIR`
  - Automatic database path resolution (explicit → env var → default → cached)
  - Logging configuration with configurable log levels
- Thread-safe `DatabaseManager` using DuckDB read-only connections
- Support for custom database paths
- Comprehensive type hints with TypedDict models
  - `Country`, `Intblock`, `SearchResult` and supporting types exported
  - Full type coverage for better IDE support and type checking
- Custom exception hierarchy
  - `InternaciaError`: Base exception class
  - `DatabaseError`: Database-related errors
  - `NotFoundError`: Resource not found errors
  - `ValidationError`: Input validation errors
  - `DownloadError`: Database download errors
  - `VersionError`: Version-related errors
- Comprehensive logging throughout the codebase
  - Structured logging for all operations
  - Configurable log levels via environment variable
  - Debug logging for query execution and results
- Comprehensive documentation with examples
- Multi-language search support (searches across translations, native names, acronyms)
- Partial match support in search queries
- Comprehensive test suite with 104+ tests covering all public APIs
  - 100% coverage of all public methods
  - Tests for success cases, error scenarios, and edge cases
  - Validation tests for all input parameters
  - Connection management and error handling tests
  - See [TEST_COVERAGE_ANALYSIS.md](TEST_COVERAGE_ANALYSIS.md) for detailed coverage report

### Technical Details

- Built on DuckDB for high-performance queries
- Thread-safe connection handling
- Support for Python 3.8+
- Type hints throughout the codebase with TypedDict models
- Pre-commit hooks for code quality (black, ruff, mypy, pytest)
- MIT License

