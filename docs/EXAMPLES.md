# Internacia Python SDK - Examples

Practical examples demonstrating various use cases of the Internacia Python SDK.

## Table of Contents

- [Basic Examples](#basic-examples)
- [Country Queries](#country-queries)
- [International Block Queries](#international-block-queries)
- [Search Examples](#search-examples)
- [Multi-Language Examples](#multi-language-examples)
- [Data Analysis Examples](#data-analysis-examples)
- [Integration Examples](#integration-examples)

---

## Basic Examples

### Simple Country Lookup

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Get a country by code
country = client.countries.get_by_code("US")
print(f"Country: {country['name']}")
print(f"Code: {country['code']}")
print(f"ISO3: {country['iso3code']}")
```

### Simple Block Lookup

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Get an international block
block = client.intblocks.get_by_id("EU")
print(f"Block: {block['name']}")
print(f"ID: {block['id']}")
print(f"Types: {block['blocktype']}")
```

### Basic Search

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Search for countries and blocks
results = client.search.fuzzy("United States")
for result in results:
    print(f"{result['type']}: {result['name']}")
```

---

## Country Queries

### Find Countries by Region

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Get all European countries
european_countries = client.countries.get_by_region("ECS")

print(f"Found {len(european_countries)} European countries:")
for country in european_countries:
    print(f"  - {country['name']} ({country['code']})")
```

### Find Countries by Currency

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Get all countries using the Euro
euro_countries = client.countries.get_by_currency("EUR")

print("Countries using the Euro:")
for country in euro_countries:
    print(f"  - {country['name']}")
```

### Find Countries by Language

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Get all countries where English is spoken
english_countries = client.countries.get_by_language("eng")

print("English-speaking countries:")
for country in english_countries:
    official = any(lang.get("official") for lang in country.get("languages", []))
    status = "official" if official else "spoken"
    print(f"  - {country['name']} ({status})")
```

### Find Countries by Income Level

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Get high-income countries
high_income = client.countries.get_by_income_level("HIC")

print(f"High-income countries: {len(high_income)}")
for country in high_income[:10]:  # Show first 10
    print(f"  - {country['name']}")
```

### Find Countries by Continent

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Get all Asian countries
asian_countries = client.countries.get_by_continent("Asia")

print(f"Asian countries: {len(asian_countries)}")
for country in asian_countries:
    print(f"  - {country['name']} ({country['code']})")
```

### Get UN Members

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Get all UN member countries
un_members = client.countries.get_un_members()

print(f"UN Member Countries: {len(un_members)}")
for country in un_members:
    print(f"  - {country['name']} ({country['code']})")
```

### Analyze Country Borders

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Get a country and its borders
country = client.countries.get_by_code("US")
if country and country.get("borders"):
    print(f"{country['name']} borders:")
    for border_code in country["borders"]:
        border_country = client.countries.get_by_code(border_code)
        if border_country:
            print(f"  - {border_country['name']} ({border_code})")
```

### Find Countries with Multiple Currencies

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Find countries with multiple currencies
all_countries = client.countries.get_all()
multi_currency = [
    c for c in all_countries
    if len(c.get("currencies", [])) > 1
]

print(f"Countries with multiple currencies: {len(multi_currency)}")
for country in multi_currency[:10]:
    currencies = [curr["code"] for curr in country.get("currencies", [])]
    print(f"  - {country['name']}: {', '.join(currencies)}")
```

---

## International Block Queries

### Find Blocks by Type

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Get all economic blocks
economic_blocks = client.intblocks.get_by_blocktype("economic")

print(f"Economic blocks: {len(economic_blocks)}")
for block in economic_blocks:
    print(f"  - {block['name']} ({block['id']})")
```

### Find Blocks by Member Country

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Get all blocks that include the United States
us_blocks = client.intblocks.get_by_member("US")

print("International blocks including the United States:")
for block in us_blocks:
    print(f"  - {block['name']} ({block['id']})")
    print(f"    Types: {', '.join(block.get('blocktype', []))}")
```

### Find Blocks by Geographic Scope

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Get all global organizations
global_blocks = client.intblocks.get_by_geographic_scope("global")

print(f"Global organizations: {len(global_blocks)}")
for block in global_blocks:
    print(f"  - {block['name']} ({block['id']})")
```

### Find Blocks Founded in a Year

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Get blocks founded in 1993
blocks_1993 = client.intblocks.get_by_founded_year(1993)

print("Blocks founded in 1993:")
for block in blocks_1993:
    print(f"  - {block['name']} ({block['id']})")
    if block.get("founded"):
        print(f"    Founded: {block['founded']}")
```

### Find Blocks by Tag

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Get blocks tagged with "trade"
trade_blocks = client.intblocks.get_by_tag("trade")

print("Trade-related blocks:")
for block in trade_blocks:
    print(f"  - {block['name']} ({block['id']})")
    print(f"    Tags: {', '.join(block.get('tags', []))}")
```

### Analyze Block Members

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Get a block and analyze its members
block = client.intblocks.get_by_id("EU")
if block and block.get("includes"):
    print(f"{block['name']} Members:")
    print(f"Total members: {len(block['includes'])}")
    
    for member in block["includes"]:
        print(f"  - {member['name']} ({member['id']})")
        if member.get("status"):
            print(f"    Status: {member['status']}")
```

---

## Search Examples

### Basic Fuzzy Search

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Search for "United States"
results = client.search.fuzzy("United States", limit=10)

print("Search results:")
for i, result in enumerate(results, 1):
    result_type = result.get("type", "unknown")
    name = result.get("name", "Unknown")
    print(f"{i}. [{result_type}] {name}")
```

### Search Only Countries

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Search only countries
countries = client.search.search_countries("United", limit=5)

print("Countries matching 'United':")
for country in countries:
    print(f"  - {country['name']} ({country['code']})")
```

### Search Only Blocks

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Search only blocks
blocks = client.search.search_intblocks("EU", limit=5)

print("Blocks matching 'EU':")
for block in blocks:
    print(f"  - {block['name']} ({block['id']})")
```

### Search by Code

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Search by country code
results = client.search.fuzzy("US", limit=5)

print("Results for 'US':")
for result in results:
    if result.get("type") == "country":
        print(f"  Country: {result['name']} ({result['code']})")
    elif result.get("type") == "intblock":
        print(f"  Block: {result['name']} ({result['id']})")
```

### Search with Custom Scope

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Search only countries, not blocks
results = client.search.fuzzy(
    "Europe",
    limit=10,
    search_countries=True,
    search_intblocks=False
)

print("Countries matching 'Europe':")
for result in results:
    if result.get("type") == "country":
        print(f"  - {result['name']}")
```

---

## Multi-Language Examples

### Search in Russian

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Search using Russian text
results = client.search.fuzzy("Россия", limit=5)

print("Search results for 'Россия' (Russia):")
for result in results:
    print(f"  - {result['name']} ({result.get('code', result.get('id'))})")
```

### Search in Chinese

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Search using Chinese characters
results = client.search.fuzzy("欧盟", limit=5)

print("Search results for '欧盟' (European Union):")
for result in results:
    print(f"  - {result['name']} ({result.get('id', result.get('code'))})")
```

### Search in Multiple Languages

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Search for Germany in different languages
queries = [
    "Germany",      # English
    "Deutschland",  # German
    "Allemagne",    # French
    "Alemania",     # Spanish
]

for query in queries:
    results = client.search.fuzzy(query, limit=1)
    if results:
        print(f"'{query}' -> {results[0]['name']}")
```

### Access Native Names

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Get a country and display native names
country = client.countries.get_by_code("DE")
if country and country.get("native_names"):
    print(f"Native names for {country['name']}:")
    for lang_code, names in country["native_names"].items():
        common = names.get("common", "")
        official = names.get("official", "")
        print(f"  {lang_code}:")
        print(f"    Common: {common}")
        print(f"    Official: {official}")
```

### Search Block Translations

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Get a block and display translations
block = client.intblocks.get_by_id("EU")
if block and block.get("translations"):
    print(f"Translations for {block['name']}:")
    for translation in block["translations"]:
        lang = translation.get("lang", "")
        name = translation.get("name", "")
        print(f"  {lang}: {name}")
```

---

## Data Analysis Examples

### Count Countries by Region

```python
from internacia import InternaciaClient
from collections import Counter

client = InternaciaClient()

# Count countries by region
all_countries = client.countries.get_all()
regions = [
    c.get("region", {}).get("value", "Unknown")
    for c in all_countries
    if c.get("region")
]

region_counts = Counter(regions)
print("Countries by region:")
for region, count in region_counts.most_common():
    print(f"  {region}: {count}")
```

### Analyze Currency Usage

```python
from internacia import InternaciaClient
from collections import Counter

client = InternaciaClient()

# Count currency usage
all_countries = client.countries.get_all()
currencies = []
for country in all_countries:
    for currency in country.get("currencies", []):
        currencies.append(currency.get("code", ""))

currency_counts = Counter(currencies)
print("Most used currencies:")
for currency, count in currency_counts.most_common(10):
    print(f"  {currency}: {count} countries")
```

### Find Most Common Languages

```python
from internacia import InternaciaClient
from collections import Counter

client = InternaciaClient()

# Count language usage
all_countries = client.countries.get_all()
languages = []
for country in all_countries:
    for lang in country.get("languages", []):
        languages.append(lang.get("code", ""))

language_counts = Counter(languages)
print("Most spoken languages:")
for lang, count in language_counts.most_common(10):
    print(f"  {lang}: {count} countries")
```

### Analyze Block Types

```python
from internacia import InternaciaClient
from collections import Counter

client = InternaciaClient()

# Count block types
all_blocks = client.intblocks.get_all()
block_types = []
for block in all_blocks:
    block_types.extend(block.get("blocktype", []))

type_counts = Counter(block_types)
print("Block types distribution:")
for blocktype, count in type_counts.most_common():
    print(f"  {blocktype}: {count} blocks")
```

### Find Countries with Most Borders

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Find countries with most borders
all_countries = client.countries.get_all()
countries_with_borders = [
    (c["name"], len(c.get("borders", [])))
    for c in all_countries
    if c.get("borders")
]

countries_with_borders.sort(key=lambda x: x[1], reverse=True)
print("Countries with most borders:")
for name, border_count in countries_with_borders[:10]:
    print(f"  {name}: {border_count} borders")
```

---

## Integration Examples

### Export to JSON

```python
import json
from internacia import InternaciaClient

client = InternaciaClient()

# Get countries and export to JSON
countries = client.countries.get_all(limit=10)

with open("countries.json", "w", encoding="utf-8") as f:
    json.dump(countries, f, indent=2, ensure_ascii=False)

print("Exported countries to countries.json")
```

### Export to CSV

```python
import csv
from internacia import InternaciaClient

client = InternaciaClient()

# Export countries to CSV
countries = client.countries.get_all(limit=10)

with open("countries.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["code", "name", "iso3code", "numeric_code"])
    writer.writeheader()
    for country in countries:
        writer.writerow({
            "code": country.get("code", ""),
            "name": country.get("name", ""),
            "iso3code": country.get("iso3code", ""),
            "numeric_code": country.get("numeric_code", ""),
        })

print("Exported countries to countries.csv")
```

### Create a Country Lookup Dictionary

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Create lookup dictionaries
all_countries = client.countries.get_all()

# By code
by_code = {c["code"]: c for c in all_countries}

# By name
by_name = {c["name"]: c for c in all_countries}

# By ISO3
by_iso3 = {c["iso3code"]: c for c in all_countries}

# Usage
us = by_code["US"]
france = by_name["France"]
usa = by_iso3["USA"]

print(f"US: {us['name']}")
print(f"France: {france['code']}")
print(f"USA: {usa['name']}")
```

### Build a Country Network Graph

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Build a graph of country borders
all_countries = client.countries.get_all()
border_graph = {}

for country in all_countries:
    code = country.get("code")
    borders = country.get("borders", [])
    if code and borders:
        border_graph[code] = borders

# Find countries that border a specific country
def find_neighbors(country_code):
    return border_graph.get(country_code, [])

# Example: Find neighbors of France
france_neighbors = find_neighbors("FR")
print("Countries bordering France:")
for neighbor_code in france_neighbors:
    neighbor = client.countries.get_by_code(neighbor_code)
    if neighbor:
        print(f"  - {neighbor['name']}")
```

### Filter and Transform Data

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Get European countries and transform data
european_countries = client.countries.get_by_continent("Europe")

# Create simplified data structure
simplified = [
    {
        "code": c["code"],
        "name": c["name"],
        "capital": c.get("capital_city", {}).get("name", ""),
        "currency": c.get("currencies", [{}])[0].get("code", "") if c.get("currencies") else "",
    }
    for c in european_countries
]

print("European countries (simplified):")
for country in simplified[:10]:
    print(f"  {country['name']} ({country['code']})")
    print(f"    Capital: {country['capital']}")
    print(f"    Currency: {country['currency']}")
```

---

## Advanced Examples

### Batch Processing

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Process multiple countries in batch
country_codes = ["US", "FR", "DE", "GB", "JP", "CN", "RU", "BR", "IN", "AU"]

countries_data = []
for code in country_codes:
    country = client.countries.get_by_code(code)
    if country:
        countries_data.append({
            "code": country["code"],
            "name": country["name"],
            "region": country.get("region", {}).get("value", ""),
            "income": country.get("incomeLevel", {}).get("value", ""),
        })

print("Batch processed countries:")
for data in countries_data:
    print(f"  {data['name']}: {data['region']}, {data['income']}")
```

### Error Handling in Loops

```python
from internacia import InternaciaClient
from internacia.exceptions import ValidationError

client = InternaciaClient()

# Process codes with error handling
codes = ["US", "XX", "FR", "123", "DE"]

for code in codes:
    try:
        country = client.countries.get_by_code(code)
        if country:
            print(f"✓ {code}: {country['name']}")
        else:
            print(f"✗ {code}: Not found")
    except ValidationError as e:
        print(f"✗ {code}: Invalid format - {e}")
```

### Combine Multiple Queries

```python
from internacia import InternaciaClient

client = InternaciaClient()

# Find countries that are:
# - In Europe
# - High income
# - UN members
# - Use the Euro

european = set(c["code"] for c in client.countries.get_by_continent("Europe"))
high_income = set(c["code"] for c in client.countries.get_by_income_level("HIC"))
un_members = set(c["code"] for c in client.countries.get_un_members())
euro_users = set(c["code"] for c in client.countries.get_by_currency("EUR"))

# Find intersection
matching = european & high_income & un_members & euro_users

print("European, high-income, UN member countries using the Euro:")
for code in sorted(matching):
    country = client.countries.get_by_code(code)
    if country:
        print(f"  - {country['name']} ({code})")
```

