# Internacia Python SDK - Quick Reference

Quick reference card for common operations and patterns.

## Installation

```bash
pip install internacia
pip install internacia[progress]  # With progress bars
```

## Initialization

```python
from internacia import InternaciaClient

# Default location
client = InternaciaClient()

# Custom path
from pathlib import Path
client = InternaciaClient(db_path=Path("/path/to/db.duckdb"))
```

## Countries

### Lookup by Code

```python
# Alpha-2 (2-letter)
country = client.countries.get_by_code("US")

# Alpha-3 (3-letter)
country = client.countries.get_by_iso3("USA")

# Numeric
country = client.countries.get_by_numeric_code("840")
```

### Query Methods

```python
# All countries
all = client.countries.get_all()
all = client.countries.get_all(limit=10)

# By attributes
by_region = client.countries.get_by_region("NAC")
by_income = client.countries.get_by_income_level("HIC")
by_continent = client.countries.get_by_continent("Europe")
by_currency = client.countries.get_by_currency("EUR")
by_language = client.countries.get_by_language("eng")

# Special queries
un_members = client.countries.get_un_members()
independent = client.countries.get_independent()

# Count
total = client.countries.count()
```

## International Blocks

### Lookup

```python
# By ID
block = client.intblocks.get_by_id("EU")
```

### Query Methods

```python
# All blocks
all = client.intblocks.get_all()
all = client.intblocks.get_all(limit=10)

# By attributes
by_type = client.intblocks.get_by_blocktype("economic")
by_status = client.intblocks.get_by_status("formal")
by_scope = client.intblocks.get_by_geographic_scope("global")
by_member = client.intblocks.get_by_member("US")
by_acronym = client.intblocks.get_by_acronym("EU")
by_tag = client.intblocks.get_by_tag("trade")
by_topic = client.intblocks.get_by_topic("economy")
by_year = client.intblocks.get_by_founded_year(1993)

# Count
total = client.intblocks.count()
```

## Search

### Basic Search

```python
# Search both
results = client.search.fuzzy("United States")

# Search only countries
countries = client.search.search_countries("United")

# Search only blocks
blocks = client.search.search_intblocks("EU")
```

### Search Options

```python
# With limit
results = client.search.fuzzy("Europe", limit=5)

# Control scope
results = client.search.fuzzy(
    "EU",
    search_countries=False,
    search_intblocks=True
)
```

### Multi-Language

```python
# Russian
results = client.search.fuzzy("Россия")

# Chinese
results = client.search.fuzzy("欧盟")

# French
results = client.search.fuzzy("UE")
```

## Database Management

### Download

```python
from internacia import download_database

# Latest
db_path = download_database()

# Specific version
db_path = download_database(version="v1.0.0")

# Force re-download
db_path = download_database(force=True)
```

### Updates

```python
from internacia import check_for_updates, get_latest_version

# Check for updates
info = check_for_updates()
if info["has_update"]:
    download_database()

# Get latest version
latest = get_latest_version()
```

### Cache

```python
from internacia import get_cache_dir, get_cached_database_path

# Cache directory
cache_dir = get_cache_dir()

# Cached database path
latest_path = get_cached_database_path()
version_path = get_cached_database_path(version="v1.0.0")
```

## Data Access Patterns

### Country Data

```python
country = client.countries.get_by_code("US")

# Basic
name = country["name"]
code = country["code"]

# Nested
capital = country["capital_city"]["name"]
region = country["region"]["value"]
income = country["incomeLevel"]["value"]

# Lists
languages = [lang["name"] for lang in country["languages"]]
currencies = [curr["code"] for curr in country["currencies"]]

# Native names
for lang, names in country["native_names"].items():
    print(f"{lang}: {names['common']}")
```

### Block Data

```python
block = client.intblocks.get_by_id("EU")

# Basic
name = block["name"]
id = block["id"]
status = block["status"]

# Lists
types = block["blocktype"]
tags = block["tags"]

# Nested lists
for translation in block["translations"]:
    print(f"{translation['lang']}: {translation['name']}")

for member in block["includes"]:
    print(f"{member['name']} ({member['id']})")
```

### Search Results

```python
results = client.search.fuzzy("United States")

for result in results:
    if result["type"] == "country":
        print(f"Country: {result['name']}")
    elif result["type"] == "intblock":
        print(f"Block: {result['name']}")
```

## Error Handling

```python
from internacia.exceptions import (
    ValidationError,
    NotFoundError,
    DatabaseError,
)

try:
    country = client.countries.get_by_code("US")
except ValidationError as e:
    print(f"Invalid input: {e}")
except DatabaseError as e:
    print(f"Database error: {e}")
```

## Common Patterns

### Check for None

```python
country = client.countries.get_by_code("XX")
if country:
    print(country["name"])
else:
    print("Not found")
```

### Filter Results

```python
# Filter countries
european = client.countries.get_by_continent("Europe")
high_income = [c for c in european if c.get("incomeLevel", {}).get("id") == "HIC"]
```

### Batch Processing

```python
codes = ["US", "FR", "DE", "GB"]
countries = []
for code in codes:
    country = client.countries.get_by_code(code)
    if country:
        countries.append(country)
```

### Count and Statistics

```python
# Count by region
from collections import Counter
all_countries = client.countries.get_all()
regions = [c.get("region", {}).get("value") for c in all_countries if c.get("region")]
region_counts = Counter(regions)
```

## Type Hints

```python
from internacia import Country, Intblock, SearchResult

country: Country = client.countries.get_by_code("US")
block: Intblock = client.intblocks.get_by_id("EU")
results: list[SearchResult] = client.search.fuzzy("test")
```

## Environment Variables

```bash
# Database path
export INTERNACIA_DB_PATH="/path/to/db.duckdb"

# Log level
export INTERNACIA_LOG_LEVEL="DEBUG"

# Cache directory
export INTERNACIA_CACHE_DIR="/path/to/cache"
```

## Return Types

All functions return pure Python types:
- **Dictionaries**: `dict` (TypedDict for type hints)
- **Lists**: `list`
- **Integers**: `int`
- **None**: `None` for optional values
- **Path**: `pathlib.Path` for paths

**No numpy arrays or pandas DataFrames are returned.**

## Common Region IDs

- `NAC`: North America
- `ECS`: Europe and Central Asia
- `SSF`: Sub-Saharan Africa
- `MEA`: Middle East and North Africa
- `EAS`: East Asia and Pacific
- `SAS`: South Asia
- `LCN`: Latin America and Caribbean

## Common Income Level IDs

- `OEC`: High income: OECD
- `HIC`: High income: nonOECD
- `UMC`: Upper middle income
- `LMC`: Lower middle income
- `LIC`: Low income

## Common Block Types

- `economic`: Economic organizations
- `political`: Political organizations
- `military`: Military alliances
- `cultural`: Cultural organizations
- `environmental`: Environmental organizations

## Thread Safety

The SDK is thread-safe. You can safely use the same client instance from multiple threads:

```python
import threading

def query(code):
    country = client.countries.get_by_code(code)
    print(f"{code}: {country['name']}")

threads = [threading.Thread(target=query, args=(code,)) for code in ["US", "FR", "DE"]]
for t in threads:
    t.start()
for t in threads:
    t.join()
```

## Performance Tips

1. **Use specific queries** instead of broad searches
2. **Set appropriate limits** for search results
3. **Reuse client instance** instead of creating multiple
4. **Cache frequently accessed data** when appropriate
5. **Use appropriate search scope** (countries vs blocks)

## See Also

- [API Reference](API_REFERENCE.md) - Complete API documentation
- [User Guide](GUIDE.md) - Comprehensive usage guide
- [Examples](EXAMPLES.md) - Code examples
- [Main README](../README.md) - Installation and setup

