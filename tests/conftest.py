"""Pytest configuration and fixtures."""

from unittest.mock import Mock

import duckdb
import pytest

from internacia.database import DatabaseManager


def make_meta_db(path, version="3.0.0", contract_version=None):
    """Create a DuckDB file with only a ``_meta`` table (one row per dataset)."""
    con = duckdb.connect(str(path))
    try:
        extra = ", contract_version VARCHAR" if contract_version is not None else ""
        con.execute(
            "CREATE TABLE _meta (dataset VARCHAR, version VARCHAR, build_date VARCHAR, "
            "git_commit VARCHAR, row_count BIGINT, schema_hash VARCHAR, "
            f"data_license VARCHAR{extra})"
        )
        for dataset, rows in (("countries", 256), ("intblocks", 1269)):
            values = [dataset, version, "2026-10-16T14:30:59Z", "cd96e13", rows, "abc", "CC-BY-4.0"]
            if contract_version is not None:
                values.append(contract_version)
            con.execute(f"INSERT INTO _meta VALUES ({', '.join('?' * len(values))})", values)
    finally:
        con.close()
    return path


@pytest.fixture
def mock_db_path(tmp_path):
    """A DuckDB file with a contract 3.0 ``_meta`` table (internacia-db 3.0.0 layout)."""
    return make_meta_db(tmp_path / "test.duckdb")


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
