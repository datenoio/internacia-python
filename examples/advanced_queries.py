"""
Advanced query examples for Internacia SDK.

This script demonstrates more complex queries and data analysis.
"""

from internacia import InternaciaClient
from collections import Counter

# Initialize the client
client = InternaciaClient()

print("=" * 60)
print("Advanced Query Examples")
print("=" * 60)

# ===== Country Analysis =====
print("\n--- Country Analysis ---\n")

# Get all countries and analyze
print("1. Analyze countries by continent:")
all_countries = client.countries.get_all()
continents = []
for country in all_countries:
    if country.get('continents'):
        continents.extend(country['continents'])

continent_counts = Counter(continents)
print("   Countries by continent:")
for continent, count in continent_counts.most_common():
    print(f"   - {continent}: {count}")

# Analyze by income level
print("\n2. Analyze countries by income level:")
income_levels = {}
for country in all_countries:
    income = country.get('incomeLevel', {})
    if income:
        level = income.get('value', 'Unknown')
        income_levels[level] = income_levels.get(level, 0) + 1

print("   Countries by income level:")
for level, count in sorted(income_levels.items(), key=lambda x: x[1], reverse=True):
    print(f"   - {level}: {count}")

# Find countries with most languages
print("\n3. Countries with most languages:")
countries_with_langs = [
    (c['code'], c['name'], len(c.get('languages', [])))
    for c in all_countries
    if c.get('languages')
]
countries_with_langs.sort(key=lambda x: x[2], reverse=True)
print("   Top 5 countries by number of languages:")
for code, name, lang_count in countries_with_langs[:5]:
    print(f"   - {code} ({name}): {lang_count} languages")

# ===== Block Analysis =====
print("\n--- Block Analysis ---\n")

# Get all blocks
all_blocks = client.intblocks.get_all()

# Analyze by block type
print("1. Analyze blocks by type:")
block_types = []
for block in all_blocks:
    if block.get('blocktype'):
        block_types.extend(block['blocktype'])

type_counts = Counter(block_types)
print("   Blocks by type:")
for block_type, count in type_counts.most_common():
    print(f"   - {block_type}: {count}")

# Analyze by geographic scope
print("\n2. Analyze blocks by geographic scope:")
scopes = {}
for block in all_blocks:
    scope = block.get('geographic_scope', 'Unknown')
    scopes[scope] = scopes.get(scope, 0) + 1

print("   Blocks by geographic scope:")
for scope, count in sorted(scopes.items(), key=lambda x: x[1], reverse=True):
    print(f"   - {scope}: {count}")

# Find largest blocks by membership
print("\n3. Largest blocks by membership:")
blocks_with_members = [
    (b['id'], b['name'], b.get('membership_count', 0))
    for b in all_blocks
    if b.get('membership_count')
]
blocks_with_members.sort(key=lambda x: x[2], reverse=True)
print("   Top 10 blocks by membership:")
for block_id, name, count in blocks_with_members[:10]:
    print(f"   - {block_id} ({name}): {count} members")

# Find blocks with most acronyms
print("\n4. Blocks with most acronyms:")
blocks_with_acronyms = [
    (b['id'], b['name'], len(b.get('acronyms', [])))
    for b in all_blocks
    if b.get('acronyms')
]
blocks_with_acronyms.sort(key=lambda x: x[2], reverse=True)
print("   Top 5 blocks by number of acronyms:")
for block_id, name, acr_count in blocks_with_acronyms[:5]:
    print(f"   - {block_id} ({name}): {acr_count} acronyms")

# ===== Cross-Reference Queries =====
print("\n--- Cross-Reference Queries ---\n")

# Find countries that are members of the most blocks
print("1. Countries that are members of the most blocks:")
country_block_counts = {}
for block in all_blocks:
    if block.get('includes'):
        for member in block['includes']:
            if member.get('type') == 'country':
                country_code = member.get('id', '')
                country_block_counts[country_code] = country_block_counts.get(country_code, 0) + 1

top_countries = sorted(country_block_counts.items(), key=lambda x: x[1], reverse=True)[:10]
print("   Top 10 countries by number of block memberships:")
for country_code, count in top_countries:
    country = client.countries.get_by_code(country_code)
    country_name = country['name'] if country else country_code
    print(f"   - {country_code} ({country_name}): {count} blocks")

# Find blocks founded in recent years
print("\n2. Blocks founded in the 2000s:")
recent_blocks = []
for block in all_blocks:
    founded = block.get('founded', '')
    if founded and founded.startswith('200'):
        recent_blocks.append((block['id'], block['name'], founded))

recent_blocks.sort(key=lambda x: x[2], reverse=True)
print(f"   Found {len(recent_blocks)} blocks founded in the 2000s:")
for block_id, name, year in recent_blocks[:10]:
    print(f"   - {block_id} ({name}): {year}")

print("\n" + "=" * 60)

