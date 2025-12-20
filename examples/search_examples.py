"""
Search examples for Internacia SDK.

This script demonstrates the fuzzy search functionality.
"""

from internacia import InternaciaClient

# Initialize the client
client = InternaciaClient()

print("=" * 60)
print("Search Examples")
print("=" * 60)

# ===== Basic Search =====
print("\n--- Basic Fuzzy Search ---\n")

# Search for "United States"
print("1. Search for 'United States':")
results = client.search.fuzzy("United States", limit=5)
for result in results:
    result_type = result.get('type', 'unknown')
    if result_type == 'country':
        print(f"   Country: {result['code']} - {result['name']}")
    else:
        print(f"   Block: {result['id']} - {result['name']}")

# Search for "EU"
print("\n2. Search for 'EU':")
results = client.search.fuzzy("EU", limit=5)
for result in results:
    result_type = result.get('type', 'unknown')
    if result_type == 'country':
        print(f"   Country: {result['code']} - {result['name']}")
    else:
        print(f"   Block: {result['id']} - {result['name']}")

# ===== Country-Only Search =====
print("\n--- Country-Only Search ---\n")

print("3. Search countries for 'United':")
countries = client.search.search_countries("United", limit=5)
for country in countries:
    print(f"   {country['code']}: {country['name']}")

# ===== Block-Only Search =====
print("\n--- Block-Only Search ---\n")

print("4. Search blocks for 'Union':")
blocks = client.search.search_intblocks("Union", limit=5)
for block in blocks:
    print(f"   {block['id']}: {block['name']}")

# ===== Multi-Language Search =====
print("\n--- Multi-Language Search ---\n")

# Russian search
print("5. Search in Russian (Европа):")
results = client.search.fuzzy("Европа", limit=5)
for result in results:
    result_type = result.get('type', 'unknown')
    if result_type == 'country':
        print(f"   Country: {result['code']} - {result['name']}")
    else:
        print(f"   Block: {result['id']} - {result['name']}")

# Chinese search
print("\n6. Search in Chinese (欧盟):")
results = client.search.fuzzy("欧盟", limit=5)
for result in results:
    result_type = result.get('type', 'unknown')
    if result_type == 'country':
        print(f"   Country: {result['code']} - {result['name']}")
    else:
        print(f"   Block: {result['id']} - {result['name']}")

# French acronym
print("\n7. Search for French acronym 'UE':")
results = client.search.fuzzy("UE", limit=5)
for result in results:
    result_type = result.get('type', 'unknown')
    if result_type == 'country':
        print(f"   Country: {result['code']} - {result['name']}")
    else:
        print(f"   Block: {result['id']} - {result['name']}")

# ===== Partial Match Search =====
print("\n--- Partial Match Search ---\n")

print("8. Search for partial match 'Euro':")
results = client.search.fuzzy("Euro", limit=10)
print(f"   Found {len(results)} results")
for result in results[:5]:
    result_type = result.get('type', 'unknown')
    if result_type == 'country':
        print(f"   Country: {result['code']} - {result['name']}")
    else:
        print(f"   Block: {result['id']} - {result['name']}")

# ===== Code Search =====
print("\n--- Code Search ---\n")

print("9. Search by country code 'FR':")
results = client.search.fuzzy("FR", limit=5)
for result in results:
    result_type = result.get('type', 'unknown')
    if result_type == 'country':
        print(f"   Country: {result['code']} - {result['name']}")
    else:
        print(f"   Block: {result['id']} - {result['name']}")

print("\n" + "=" * 60)

