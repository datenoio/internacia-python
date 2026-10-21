"""
Multi-language search examples for Internacia SDK.

This script demonstrates searching in different languages.
"""

from internacia import InternaciaClient

# Initialize the client
client = InternaciaClient()

print("=" * 60)
print("Multi-Language Search Examples")
print("=" * 60)

# Define test queries in different languages
test_queries = [
    ("English", "European Union"),
    ("Russian", "Европейский союз"),
    ("Chinese (Simplified)", "欧盟"),
    ("Chinese (Traditional)", "歐盟"),
    ("French", "Union européenne"),
    ("Spanish", "Unión Europea"),
    ("German", "Europäische Union"),
    ("Italian", "Unione europea"),
    ("Portuguese", "União Europeia"),
]

print("\n--- Searching for European Union in Different Languages ---\n")

for language, query in test_queries:
    print(f"{language} ('{query}'):")
    results = client.search.fuzzy(query, limit=3)
    for result in results:
        result_type = result.get("type", "unknown")
        if result_type == "country":
            print(f"  - Country: {result['code']} - {result['name']}")
        else:
            print(f"  - Block: {result['id']} - {result['name']}")
    print()

# Test acronyms in different languages
print("\n--- Searching for Acronyms in Different Languages ---\n")

acronym_queries = [
    ("English", "EU"),
    ("French", "UE"),
    ("Russian", "ЕС"),
    ("Ukrainian", "ЄС"),
    ("Chinese", "欧盟"),
]

for language, query in acronym_queries:
    print(f"{language} acronym '{query}':")
    results = client.search.fuzzy(query, limit=3)
    for result in results:
        result_type = result.get("type", "unknown")
        if result_type == "country":
            print(f"  - Country: {result['code']} - {result['name']}")
        else:
            print(f"  - Block: {result['id']} - {result['name']}")
    print()

# Test country names in different languages
print("\n--- Searching for Countries in Different Languages ---\n")

country_queries = [
    ("English", "United States"),
    ("Spanish", "Estados Unidos"),
    ("French", "États-Unis"),
    ("German", "Vereinigte Staaten"),
    ("Russian", "Соединенные Штаты"),
    ("Chinese", "美国"),
]

for language, query in country_queries:
    print(f"{language} ('{query}'):")
    results = client.search.search_countries(query, limit=3)
    for result in results:
        print(f"  - {result['code']}: {result['name']}")
    print()

# Test partial matches in different languages
print("\n--- Partial Match Search in Different Languages ---\n")

partial_queries = [
    ("English", "Euro"),
    ("Russian", "Европ"),
    ("Chinese", "欧"),
]

for language, query in partial_queries:
    print(f"{language} partial match '{query}':")
    results = client.search.fuzzy(query, limit=5)
    print(f"  Found {len(results)} results")
    for result in results[:3]:
        result_type = result.get("type", "unknown")
        if result_type == "country":
            print(f"  - Country: {result['code']} - {result['name']}")
        else:
            print(f"  - Block: {result['id']} - {result['name']}")
    print()

print("=" * 60)
print("\nNote: The actual results may vary depending on the data available")
print("in the internacia-db dataset. Some translations may not be present")
print("for all entities.")
