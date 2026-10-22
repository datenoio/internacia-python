# Internacia Python SDK - User Guide

Comprehensive guide for using the Internacia Python SDK.

## Table of Contents

- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [Working with Countries](#working-with-countries)
- [Working with International Blocks](#working-with-international-blocks)
- [Search Functionality](#search-functionality)
- [Database Management](#database-management)
- [Error Handling](#error-handling)
- [Thread Safety](#thread-safety)
- [Best Practices](#best-practices)
- [Performance Tips](#performance-tips)

---

## Getting Started

### Installation

```bash
pip install internacia
```

For download progress bars:
```bash
pip install internacia[progress]
```

### Basic Usage

```python
from internacia import InternaciaClient

# Initialize the client
client = InternaciaClient()

# Get a country
country = client.countries.get_by_code("US")
print(country["name"])  # "United States"

# Search
results = client.search.fuzzy("United States")
```

---

## Configuration

### Database Path Resolution

The SDK resolves the database path in the following order:

1. **Explicit `db_path` parameter** in `InternaciaClient()`
2. **`INTERNACIA_DB_PATH` environment variable**
3. **Pinned cached release**: `data_version=` or `INTERNACIA_DATA_VERSION` (`~/.internacia/<tag>/internacia.duckdb`)
4. **Newest cached release** with a supported contract major (download with `download_database()`)

### Environment Variables

```bash
# Set custom database path
export INTERNACIA_DB_PATH="/path/to/internacia.duckdb"

# Set log level
export INTERNACIA_LOG_LEVEL="DEBUG"

# Set cache directory for downloads
export INTERNACIA_CACHE_DIR="/path/to/cache"
```

### Logging Configuration

```python
import logging
import os

# Set log level via environment variable
os.environ["INTERNACIA_LOG_LEVEL"] = "DEBUG"

from internacia import InternaciaClient

# Logging is automatically configured on client initialization
client = InternaciaClient()

# Or configure programmatically
logging.getLogger("internacia").setLevel(logging.DEBUG)
```

**Log Levels:**
- `DEBUG`: Detailed information (queries, results)
- `INFO`: General informational messages
- `WARNING`: Warning messages (default)
- `ERROR`: Error messages only
- `CRITICAL`: Critical errors only

---

## Working with Countries

### Finding Countries

#### By Code

```python
# ISO 3166-1 alpha-2 (2-letter code)
country = client.countries.get_by_code("US")

# ISO 3166-1 alpha-3 (3-letter code)
country = client.countries.get_by_iso3("USA")

# Numeric code
country = client.countries.get_by_numeric_code("840")
```

#### By Attributes

```python
# By region
european_countries = client.countries.get_by_region("ECS")

# By income level
high_income = client.countries.get_by_income_level("HIC")

# By continent
asian_countries = client.countries.get_by_continent("Asia")

# By currency
euro_countries = client.countries.get_by_currency("EUR")

# By language
english_speaking = client.countries.get_by_language("eng")
```

#### Special Queries

```python
# UN members
un_members = client.countries.get_un_members()

# Independent countries
independent = client.countries.get_independent()

# All countries
all_countries = client.countries.get_all()

# With limit
first_10 = client.countries.get_all(limit=10)
```

### Accessing Country Data

```python
country = client.countries.get_by_code("US")

# Basic information
print(country["name"])           # "United States"
print(country["code"])           # "US"
print(country["iso3code"])       # "USA"
print(country["numeric_code"])  # "840"

# Capital city
if country.get("capital_city"):
    capital = country["capital_city"]
    print(capital["name"])  # "Washington"
    print(capital["lat"])   # 38.9
    print(capital["lng"])   # -77.0

# Region and income level
if country.get("region"):
    print(country["region"]["value"])  # "North America"

if country.get("incomeLevel"):
    print(country["incomeLevel"]["value"])  # "High income: OECD"

# Languages
for lang in country.get("languages", []):
    print(f"{lang['name']} ({lang['code']})")

# Currencies
for currency in country.get("currencies", []):
    print(f"{currency['name']} ({currency['code']})")

# Native names (multi-language)
if country.get("native_names"):
    for lang_code, names in country["native_names"].items():
        print(f"{lang_code}: {names['common']}")

# Borders
for border_code in country.get("borders", []):
    border_country = client.countries.get_by_code(border_code)
    if border_country:
        print(f"Borders: {border_country['name']}")
```

### Working with Multiple Countries

```python
# Get all countries and process
all_countries = client.countries.get_all()

for country in all_countries:
    print(f"{country['code']}: {country['name']}")

# Filter countries
european_countries = client.countries.get_by_continent("Europe")
high_income_european = [
    c for c in european_countries
    if c.get("incomeLevel", {}).get("id") == "HIC"
]

# Group by region
from collections import defaultdict
by_region = defaultdict(list)
for country in client.countries.get_all():
    if country.get("region"):
        region_id = country["region"]["id"]
        by_region[region_id].append(country)
```

---

## Working with International Blocks

### Finding Blocks

#### By ID

```python
# Get a specific block
block = client.intblocks.get_by_id("EU")
```

#### By Attributes

```python
# By type
economic_blocks = client.intblocks.get_by_blocktype("economic")

# By status
formal_blocks = client.intblocks.get_by_status("formal")

# By geographic scope
global_blocks = client.intblocks.get_by_geographic_scope("global")

# By member country
us_blocks = client.intblocks.get_by_member("US")

# By acronym
eu_block = client.intblocks.get_by_acronym("EU")

# By tag
trade_blocks = client.intblocks.get_by_tag("trade")

# By topic
economy_blocks = client.intblocks.get_by_topic("economy")

# By founding year
blocks_1993 = client.intblocks.get_by_founded_year(1993)
```

### Accessing Block Data

```python
block = client.intblocks.get_by_id("EU")

# Basic information
print(block["id"])        # "EU"
print(block["name"])      # "European Union"
print(block["status"])    # "formal"

# Block types
for blocktype in block.get("blocktype", []):
    print(blocktype)  # "economic", "political"

# Names in other languages
for other in block.get("other_names") or []:
    print(f"{other['id']}: {other['name']}")

# Acronyms (multi-language)
for acronym in block.get("acronyms", []):
    print(f"{acronym['lang']}: {acronym['value']}")

# Member countries
for member in block.get("includes", []):
    print(f"{member['name']} ({member['id']})")

# Tags and topics
for tag in block.get("tags", []):
    print(f"Tag: {tag}")

for topic in block.get("topics", []):
    print(f"Topic: {topic['name']} ({topic['key']})")

# Founding information
if block.get("founded"):
    print(f"Founded: {block['founded']}")

# Geographic scope
if block.get("geographic_scope"):
    print(f"Scope: {block['geographic_scope']}")
```

### Finding Blocks for a Country

```python
# Get all blocks that include a specific country
country_code = "US"
blocks = client.intblocks.get_by_member(country_code)

print(f"Blocks including {country_code}:")
for block in blocks:
    print(f"  - {block['name']} ({block['id']})")
```

---

## Search Functionality

### Basic Search

```python
# Search across both countries and blocks
results = client.search.fuzzy("United States")

for result in results:
    print(f"{result['type']}: {result['name']}")
```

### Search Options

```python
# Search only countries
countries = client.search.search_countries("United")

# Search only blocks
blocks = client.search.search_intblocks("EU")

# Custom limit
results = client.search.fuzzy("Europe", limit=5)

# Control search scope
results = client.search.fuzzy(
    "EU",
    search_countries=False,
    search_intblocks=True
)
```

### Multi-Language Search

The search function supports searching in any language present in the dataset:

```python
# Russian
results = client.search.fuzzy("Россия")  # Russia

# Chinese
results = client.search.fuzzy("欧盟")    # European Union

# French acronym
results = client.search.fuzzy("UE")      # EU in French

# German
results = client.search.fuzzy("Deutschland")  # Germany
```

### Search Behavior

The fuzzy search:
- **Prioritizes exact matches**: Country codes and block IDs are matched first
- **Supports partial matches**: Searches within names, names in other languages, and acronyms
- **Case-insensitive**: Matching is not case-sensitive
- **Removes duplicates**: Automatically deduplicates results
- **Sorts by relevance**: Exact matches first, then by name length

### Advanced Search Patterns

```python
# Search by code
results = client.search.fuzzy("US")  # Finds United States

# Search by numeric code
results = client.search.fuzzy("840")  # Finds United States

# Search by partial name
results = client.search.fuzzy("United")  # Finds United States, United Kingdom, etc.

# Search by native name
results = client.search.fuzzy("Frankreich")  # Finds France (German name)

# Search by block acronym
results = client.search.fuzzy("NATO")  # Finds NATO block
```

---

## Database Management

### Downloading the Database

```python
from internacia import download_database

# Download latest version
db_path = download_database()

# Download specific version
db_path = download_database(version="v3.0.0")

# Force re-download
db_path = download_database(force=True)

# With progress bar (requires tqdm)
db_path = download_database(show_progress=True)
```

### Checking for Updates

```python
from internacia import check_for_updates, get_latest_version

# Check if updates are available
update_info = check_for_updates()
if update_info["has_update"]:
    print(f"Update available: {update_info['latest_version']}")
    download_database()

# Get latest version
latest = get_latest_version()
print(f"Latest version: {latest}")
```

### Listing Releases

```python
from internacia import list_releases

releases = list_releases()
for release in releases:
    if release["has_database"]:
        print(f"{release['version']}: {release['database_size']} bytes")
```

### Cache Management

```python
from internacia import get_cache_dir, get_cached_database_path

# Get cache directory
cache_dir = get_cache_dir()
print(f"Cache: {cache_dir}")

# Get cached database path
latest_path = get_cached_database_path()
version_path = get_cached_database_path(version="v3.0.0")
```

---

## Error Handling

### Exception Hierarchy

```python
from internacia.exceptions import (
    InternaciaError,      # Base exception
    DatabaseError,        # Database issues
    NotFoundError,        # Resource not found
    ValidationError,      # Invalid input
    DownloadError,        # Download failures
    VersionError,         # Version issues
)
```

### Handling Errors

```python
from internacia import InternaciaClient
from internacia.exceptions import (
    ValidationError,
    NotFoundError,
    DatabaseError,
)

client = InternaciaClient()

try:
    # Invalid code format
    country = client.countries.get_by_code("123")
except ValidationError as e:
    print(f"Invalid input: {e}")

try:
    # Non-existent code
    country = client.countries.get_by_code("XX")
    if country is None:
        print("Country not found")
except DatabaseError as e:
    print(f"Database error: {e}")
```

### Common Error Scenarios

```python
# Empty search query
try:
    results = client.search.fuzzy("")
except ValidationError as e:
    print(f"Error: {e}")

# Invalid limit
try:
    results = client.search.fuzzy("test", limit=-1)
except ValidationError as e:
    print(f"Error: {e}")

# Database not found
try:
    client = InternaciaClient(db_path=Path("/nonexistent/path"))
except FileNotFoundError as e:
    print(f"Database not found: {e}")
```

---

## Thread Safety

The SDK is thread-safe. Each query uses its own read-only DuckDB connection.

### Concurrent Access Example

```python
import threading
from internacia import InternaciaClient

client = InternaciaClient()

def query_country(code):
    country = client.countries.get_by_code(code)
    if country:
        print(f"{code}: {country['name']}")

# Safe to use from multiple threads
threads = []
for code in ["US", "FR", "DE", "GB", "JP"]:
    t = threading.Thread(target=query_country, args=(code,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

### Thread-Safe Search

```python
import concurrent.futures
from internacia import InternaciaClient

client = InternaciaClient()

queries = ["United States", "France", "Germany", "Japan"]

def search(query):
    return client.search.fuzzy(query, limit=5)

# Parallel searches
with concurrent.futures.ThreadPoolExecutor() as executor:
    results = list(executor.map(search, queries))

for query, result in zip(queries, results):
    print(f"{query}: {len(result)} results")
```

---

## Best Practices

### 1. Check for None

Always check if a result is `None` before accessing it:

```python
country = client.countries.get_by_code("XX")
if country:
    print(country["name"])
else:
    print("Country not found")
```

### 2. Use Type Hints

Take advantage of type hints for better IDE support:

```python
from internacia import InternaciaClient, Country, Intblock

client = InternaciaClient()

country: Country = client.countries.get_by_code("US")
block: Intblock = client.intblocks.get_by_id("EU")
```

### 3. Handle Errors Gracefully

```python
from internacia.exceptions import ValidationError

try:
    country = client.countries.get_by_code("US")
except ValidationError as e:
    print(f"Invalid code: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 4. Use Limits for Large Queries

```python
# Good: Use limit for large result sets
countries = client.countries.get_all(limit=100)

# Avoid: Loading all data if you only need a subset
# all_countries = client.countries.get_all()  # May be very large
```

### 5. Cache Results When Appropriate

```python
# Cache frequently accessed data
un_members_cache = client.countries.get_un_members()

# Reuse cached data
for country in un_members_cache:
    # Process country
    pass
```

---

## Performance Tips

### 1. Use Specific Queries

Prefer specific queries over broad searches:

```python
# Fast: Direct lookup
country = client.countries.get_by_code("US")

# Slower: Broad search
results = client.search.fuzzy("US")
```

### 2. Limit Search Results

Always use appropriate limits for searches:

```python
# Good: Limited results
results = client.search.fuzzy("United", limit=10)

# Avoid: Unlimited results (may be slow)
# results = client.search.fuzzy("United", limit=1000)
```

### 3. Batch Operations

For multiple queries, consider batching:

```python
# Process multiple countries
codes = ["US", "FR", "DE", "GB"]
countries = []
for code in codes:
    country = client.countries.get_by_code(code)
    if country:
        countries.append(country)
```

### 4. Reuse Client Instance

Create one client instance and reuse it:

```python
# Good: Reuse client
client = InternaciaClient()
country1 = client.countries.get_by_code("US")
country2 = client.countries.get_by_code("FR")

# Avoid: Creating multiple clients
# client1 = InternaciaClient()
# client2 = InternaciaClient()
```

### 5. Use Appropriate Search Scope

Limit search scope when possible:

```python
# If you only need countries, don't search blocks
countries = client.search.search_countries("United")

# Instead of:
# results = client.search.fuzzy("United")  # Searches both
```

---

## Examples

See the `examples/` directory for more detailed examples:

- `basic_usage.py`: Basic operations
- `search_examples.py`: Search functionality
- `advanced_queries.py`: Complex queries
- `multi_language.py`: Multi-language search examples

