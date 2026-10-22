"""Tests for main client."""

import logging
from unittest.mock import patch

import duckdb
import pytest

from internacia.client import InternaciaClient
from internacia.countries import CountriesClient
from internacia.exceptions import ContractError
from internacia.intblocks import IntblocksClient
from internacia.search import SearchClient
from tests.conftest import make_meta_db


def test_client_init_with_db_path(mock_db_path):
    """Test client initialization with explicit db_path."""
    client = InternaciaClient(db_path=mock_db_path)
    assert client._db_manager.db_path == mock_db_path
    assert client.countries is not None
    assert client.intblocks is not None
    assert client.search is not None


def test_client_init_with_env_var(mock_db_path, monkeypatch):
    """Test client initialization with environment variable."""
    monkeypatch.setenv("INTERNACIA_DB_PATH", str(mock_db_path))
    client = InternaciaClient()
    assert client._db_manager.db_path == mock_db_path


def test_client_init_env_var_not_found(monkeypatch):
    """Test client raises error when env var points to non-existent file."""
    monkeypatch.setenv("INTERNACIA_DB_PATH", "/nonexistent/path.duckdb")
    with pytest.raises(FileNotFoundError):
        InternaciaClient()


def test_client_init_no_db_found(tmp_path, monkeypatch):
    """Test client raises error when no database found."""
    # Remove env var if set
    monkeypatch.delenv("INTERNACIA_DB_PATH", raising=False)

    # Mock parent directory to not contain internacia-db
    with patch("internacia.client.Path.exists", return_value=False):
        with pytest.raises(FileNotFoundError) as exc_info:
            InternaciaClient()
        assert "Could not find" in str(exc_info.value)


def test_client_init_db_path_not_exists(mock_db_path):
    """Test client raises error when explicit db_path doesn't exist."""
    non_existent = mock_db_path.parent / "nonexistent.duckdb"
    with pytest.raises(FileNotFoundError) as exc_info:
        InternaciaClient(db_path=non_existent)
    assert "not found at specified path" in str(exc_info.value)


def test_client_init_with_data_dir(mock_db_path, tmp_path):
    """Test client initialization with data_dir parameter."""
    # data_dir is currently not used in the implementation, but we test it doesn't break
    client = InternaciaClient(db_path=mock_db_path, data_dir=tmp_path)
    assert client._db_manager.db_path == mock_db_path  # pylint: disable=protected-access
    assert client.countries is not None
    assert client.intblocks is not None
    assert client.search is not None


def test_client_attributes(mock_db_path):
    """Test that client has all expected attributes."""
    client = InternaciaClient(db_path=mock_db_path)

    assert hasattr(client, "_db_manager")
    assert hasattr(client, "countries")
    assert hasattr(client, "intblocks")
    assert hasattr(client, "search")

    # Test that attributes are the correct types
    assert isinstance(client.countries, CountriesClient)
    assert isinstance(client.intblocks, IntblocksClient)
    assert isinstance(client.search, SearchClient)


def test_meta_derives_contract_version_for_3_0_0(mock_db_path):
    """internacia-db 3.0.0 has no contract_version column; MAJOR.MINOR of version is used."""
    meta = InternaciaClient(db_path=mock_db_path).meta()
    assert meta["version"] == "3.0.0"
    assert meta["contract_version"] == "3.0"
    assert meta["datasets"]["countries"] == {"row_count": 256, "schema_hash": "abc"}


def test_meta_reads_contract_version(tmp_path):
    db = make_meta_db(tmp_path / "db.duckdb", version="3.0.7", contract_version="3.0")
    meta = InternaciaClient(db_path=db).meta()
    meta["datasets"]["countries"]["row_count"] = 0
    assert InternaciaClient(db_path=db).meta()["datasets"]["countries"]["row_count"] == 256


def test_unsupported_contract_major_is_rejected(tmp_path):
    db = make_meta_db(tmp_path / "db.duckdb", version="4.0.0", contract_version="4.0")
    with pytest.raises(ContractError, match="requires contract 3.x"):
        InternaciaClient(db_path=db)
    assert InternaciaClient(db_path=db, check_contract=False).meta()["contract_version"] == "4.0"


def test_newer_contract_minor_warns(tmp_path, caplog):
    db = make_meta_db(tmp_path / "db.duckdb", version="3.9.0", contract_version="3.9")
    with caplog.at_level(logging.WARNING, logger="internacia.contract"):
        InternaciaClient(db_path=db)
    assert "newer than" in caplog.text


def test_database_without_meta_is_rejected(tmp_path):
    db = tmp_path / "empty.duckdb"
    duckdb.connect(str(db)).close()
    with pytest.raises(ContractError, match="_meta"):
        InternaciaClient(db_path=db)


def test_client_uses_pinned_cached_release(tmp_path, monkeypatch):
    monkeypatch.delenv("INTERNACIA_DB_PATH", raising=False)
    monkeypatch.setenv("INTERNACIA_CACHE_DIR", str(tmp_path))
    for tag in ("v3.0.0", "v3.1.0"):
        (tmp_path / tag).mkdir()
        make_meta_db(tmp_path / tag / "internacia.duckdb", version=tag[1:])
    assert InternaciaClient(data_version="3.0.0").meta()["version"] == "3.0.0"
    assert InternaciaClient().meta()["version"] == "3.1.0"
    with pytest.raises(FileNotFoundError, match="download_database\\('3.5.0'\\)"):
        InternaciaClient(data_version="3.5.0")
