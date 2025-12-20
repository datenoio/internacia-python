#!/bin/bash
# Script to update the internacia-db database

set -e

echo "Updating internacia-db database..."
echo "===================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Default path: sibling directory to internacia-python
INTERNACIA_DB_DIR="$PROJECT_ROOT/../internacia-db"

# Check if INTERNACIA_DB_DIR environment variable is set
if [ -n "$INTERNACIA_DB_DIR" ] && [ -d "$INTERNACIA_DB_DIR" ]; then
    DB_DIR="$INTERNACIA_DB_DIR"
elif [ -d "$INTERNACIA_DB_DIR" ]; then
    DB_DIR="$INTERNACIA_DB_DIR"
else
    echo "Error: internacia-db directory not found at: $INTERNACIA_DB_DIR"
    echo ""
    echo "Please either:"
    echo "  1. Ensure internacia-db is cloned as a sibling directory to internacia-python"
    echo "  2. Set INTERNACIA_DB_DIR environment variable to the path of internacia-db"
    exit 1
fi

echo "Using internacia-db directory: $DB_DIR"
echo ""

# Navigate to internacia-db directory
cd "$DB_DIR"

# Check if it's a git repository
if [ ! -d ".git" ]; then
    echo "Warning: $DB_DIR does not appear to be a git repository"
    echo "Skipping git pull..."
else
    echo "Pulling latest changes from internacia-db..."
    git pull origin main || git pull origin master || echo "Warning: Could not pull latest changes"
    echo ""
fi

# Check if builder script exists
BUILDER_SCRIPT="$DB_DIR/scripts/builder.py"
if [ ! -f "$BUILDER_SCRIPT" ]; then
    echo "Error: builder.py not found at: $BUILDER_SCRIPT"
    exit 1
fi

# Rebuild the database
echo "Rebuilding DuckDB database..."
python3 "$BUILDER_SCRIPT" build --formats duckdb

# Verify the database file exists
DB_FILE="$DB_DIR/data/datasets/internacia.duckdb"
if [ -f "$DB_FILE" ]; then
    DB_SIZE=$(ls -lh "$DB_FILE" | awk '{print $5}')
    echo ""
    echo "===================================="
    echo "Database update complete!"
    echo ""
    echo "Database location: $DB_FILE"
    echo "Database size: $DB_SIZE"
    echo ""
    echo "The SDK will automatically use the updated database on next initialization."
else
    echo ""
    echo "Warning: Database file not found at expected location: $DB_FILE"
    echo "The build may have failed or the database is in a different location."
    exit 1
fi

