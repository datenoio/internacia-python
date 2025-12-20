# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

