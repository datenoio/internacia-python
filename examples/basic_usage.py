"""
Basic usage examples for Internacia SDK.

This script demonstrates basic operations with countries and international blocks.
"""

from internacia import InternaciaClient

# Initialize the client
client = InternaciaClient()

print("=" * 60)
print("Basic Usage Examples")
print("=" * 60)

# ===== Countries =====
print("\n--- Countries ---\n")

# Get a country by code
print("1. Get country by code:")
country = client.countries.get_by_code("US")
if country:
    print(f"   Code: {country['code']}")
    print(f"   Name: {country['name']}")
    print(f"   Official Name: {country.get('official_name', 'N/A')}")
    print(f"   Capital: {(country.get('capital_city') or {}).get('name', 'N/A')}")

# Get country by ISO3 code
print("\n2. Get country by ISO3 code:")
country = client.countries.get_by_iso3("FRA")
if country:
    print(f"   {country['code']}: {country['name']}")

# Get countries by region
print("\n3. Get countries by region (North America):")
countries = client.countries.get_by_region("NAC")
print(f"   Found {len(countries)} countries")
for c in countries[:5]:  # Show first 5
    print(f"   - {c['code']}: {c['name']}")

# Get UN members
print("\n4. Get UN member countries:")
un_members = client.countries.get_un_members()
print(f"   Total UN members: {len(un_members)}")

# Get countries by currency
print("\n5. Get countries using EUR:")
eur_countries = client.countries.get_by_currency("EUR")
print(f"   Found {len(eur_countries)} countries using EUR")
for c in eur_countries[:5]:
    print(f"   - {c['code']}: {c['name']}")

# ===== International Blocks =====
print("\n--- International Blocks ---\n")

# Get a block by ID
print("1. Get block by ID:")
block = client.intblocks.get_by_id("EU")
if block:
    print(f"   ID: {block['id']}")
    print(f"   Name: {block['name']}")
    print(f"   Type: {', '.join(block.get('blocktype') or [])}")
    print(f"   Status: {block.get('status', 'N/A')}")
    print(f"   Members: {block.get('membership_count', 'N/A')}")

# Get blocks by type
print("\n2. Get economic blocks:")
economic_blocks = client.intblocks.get_by_blocktype("economic")
print(f"   Found {len(economic_blocks)} economic blocks")
for b in economic_blocks[:5]:
    print(f"   - {b['id']}: {b['name']}")

# Get blocks containing a country
print("\n3. Get blocks containing US:")
us_blocks = client.intblocks.get_by_member("US")
print(f"   US is a member of {len(us_blocks)} blocks")
for b in us_blocks[:5]:
    print(f"   - {b['id']}: {b['name']}")

# Get blocks by acronym
print("\n4. Get blocks by acronym 'EU':")
eu_blocks = client.intblocks.get_by_acronym("EU")
print(f"   Found {len(eu_blocks)} blocks with acronym 'EU'")
for b in eu_blocks:
    print(f"   - {b['id']}: {b['name']}")

# Get total counts
print("\n5. Statistics:")
print(f"   Total countries: {client.countries.count()}")
print(f"   Total blocks: {client.intblocks.count()}")

print("\n" + "=" * 60)
