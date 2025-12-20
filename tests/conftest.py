"""Pytest configuration and fixtures."""

from unittest.mock import Mock

import pytest

from internacia.database import DatabaseManager


@pytest.fixture
def mock_db_path(tmp_path):
    """Create a temporary database path for testing."""
    db_file = tmp_path / "test.duckdb"
    db_file.touch()
    return db_file


@pytest.fixture
def mock_db_manager(mock_db_path):
    """Create a mock database manager."""
    manager = Mock(spec=DatabaseManager)
    manager.db_path = mock_db_path
    manager.execute_query_dict = Mock(return_value=[])
    manager.execute_query = Mock(return_value=[])
    return manager


@pytest.fixture
def sample_country_data():
    """Sample country data for testing."""
    return {
        "code": "US",
        "name": "United States",
        "iso3code": "USA",
        "numeric_code": "840",
        "official_name": "United States of America",
        "un_member": True,
        "independent": True,
    }


@pytest.fixture
def sample_block_data():
    """Sample block data for testing."""
    return {
        "id": "EU",
        "name": "European Union",
        "blocktype": ["economic", "political"],
        "status": "formal",
        "geographic_scope": "regional",
    }
