#!/bin/bash
# Script to check dependencies for security vulnerabilities

set -e

echo "Checking dependencies for security vulnerabilities..."
echo "=================================================="

# Check if pip-audit is available
if ! command -v pip-audit &> /dev/null; then
    echo "Installing pip-audit..."
    pip install pip-audit
fi

# Run pip-audit
echo ""
echo "Running pip-audit..."
pip-audit --desc

echo ""
echo "=================================================="
echo "Dependency check complete!"
echo ""
echo "To fix vulnerabilities, update the affected packages in pyproject.toml"
echo "and run: pip install -U <package-name>"

