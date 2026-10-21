# Internacia Python SDK - Documentation

Welcome to the Internacia Python SDK documentation. This directory contains comprehensive documentation for using the SDK.

## Documentation Index

### 📚 [API Reference](API_REFERENCE.md)
Complete API reference with detailed documentation for all classes, methods, and functions.

**Contents:**
- `InternaciaClient` - Main client class
- `CountriesClient` - Country data queries
- `IntblocksClient` - International block queries
- `SearchClient` - Search functionality
- Downloader functions
- Data models and types
- Exception classes

### 📖 [User Guide](GUIDE.md)
Comprehensive guide covering all aspects of using the SDK.

**Contents:**
- Getting started
- Configuration
- Working with countries
- Working with international blocks
- Search functionality
- Database management
- Error handling
- Thread safety
- Best practices
- Performance tips

### 💡 [Examples](EXAMPLES.md)
Practical code examples demonstrating various use cases.

**Contents:**
- Basic examples
- Country queries
- International block queries
- Search examples
- Multi-language examples
- Data analysis examples
- Integration examples

### ⚡ [Quick Reference](QUICK_REFERENCE.md)
Quick reference card for common operations.

**Contents:**
- Common code snippets
- Method signatures
- Data structure quick lookup
- Common patterns

## Quick Start

1. **Install the SDK:**
   ```bash
   pip install internacia
   ```

2. **Initialize the client:**
   ```python
   from internacia import InternaciaClient
   client = InternaciaClient()
   ```

3. **Get started:**
   ```python
   # Get a country
   country = client.countries.get_by_code("US")
   
   # Search
   results = client.search.fuzzy("United States")
   
   # Get a block
   block = client.intblocks.get_by_id("EU")
   ```

## Documentation Structure

```
docs/
├── README.md              # This file - documentation index
├── API_REFERENCE.md       # Complete API reference
├── GUIDE.md               # Comprehensive user guide
├── EXAMPLES.md            # Code examples
└── QUICK_REFERENCE.md     # Quick reference card
```

## Getting Help

- **API Questions**: See [API Reference](API_REFERENCE.md)
- **How-to Questions**: See [User Guide](GUIDE.md)
- **Code Examples**: See [Examples](EXAMPLES.md)
- **Quick Lookup**: See [Quick Reference](QUICK_REFERENCE.md)

## Additional Resources

- **Main README**: See the [main README](../README.md) for installation, setup, and overview
- **Examples Directory**: See the [`examples/`](../examples/) directory for runnable example scripts
- **GitHub Repository**: [https://github.com/datenoio/internacia-python](https://github.com/datenoio/internacia-python)

## Contributing

If you find errors or want to improve the documentation, please submit a pull request or open an issue on GitHub.

