"""Extended tests for database manager."""

from unittest.mock import MagicMock, patch

import pytest

from internacia.database import DatabaseManager
from internacia.exceptions import DatabaseError


class TestDatabaseManagerExecuteQuery:
    """Test execute_query method."""

    def test_execute_query_without_parameters(self, mock_db_path):
        """Test execute_query without parameters."""
        # Create a real DuckDB connection for this test
        with patch("internacia.database.duckdb") as mock_duckdb:
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_conn
            mock_conn.execute.return_value.fetchall.return_value = [("US", "United States")]
            mock_duckdb.connect.return_value = mock_conn

            manager = DatabaseManager(mock_db_path)
            result = manager.execute_query("SELECT code, name FROM countries LIMIT 1")

            assert result == [("US", "United States")]
            mock_conn.execute.assert_called_once_with("SELECT code, name FROM countries LIMIT 1")
            mock_conn.close.assert_called_once()

    def test_execute_query_with_parameters(self, mock_db_path):
        """Test execute_query with parameters."""
        with patch("internacia.database.duckdb") as mock_duckdb:
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_conn
            mock_conn.execute.return_value.fetchall.return_value = [("US",)]
            mock_duckdb.connect.return_value = mock_conn

            manager = DatabaseManager(mock_db_path)
            result = manager.execute_query("SELECT code FROM countries WHERE code = ?", ("US",))

            assert result == [("US",)]
            mock_conn.execute.assert_called_once_with(
                "SELECT code FROM countries WHERE code = ?", ("US",)
            )

    def test_execute_query_error_handling(self, mock_db_path):
        """Test execute_query error handling."""
        with patch("internacia.database.duckdb") as mock_duckdb:
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_conn
            mock_conn.execute.side_effect = Exception("SQL syntax error")
            mock_duckdb.connect.return_value = mock_conn

            manager = DatabaseManager(mock_db_path)

            with pytest.raises(DatabaseError) as exc_info:
                manager.execute_query("INVALID SQL")

            assert "Query execution failed" in str(exc_info.value)
            mock_conn.close.assert_called_once()


class TestDatabaseManagerExecuteQueryDict:
    """Test execute_query_dict method."""

    def test_execute_query_dict_without_parameters(self, mock_db_path):
        """Test execute_query_dict without parameters."""
        with patch("internacia.database.duckdb") as mock_duckdb:
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_conn
            mock_conn.execute.return_value.description = [("code",), ("name",)]
            mock_conn.execute.return_value.fetchall.return_value = [("US", "United States")]
            mock_duckdb.connect.return_value = mock_conn

            manager = DatabaseManager(mock_db_path)
            result = manager.execute_query_dict("SELECT code, name FROM countries LIMIT 1")

            assert len(result) == 1
            assert result[0]["code"] == "US"
            assert result[0]["name"] == "United States"
            mock_conn.execute.assert_called_once()
            mock_conn.close.assert_called_once()

    def test_execute_query_dict_with_parameters(self, mock_db_path):
        """Test execute_query_dict with parameters."""
        with patch("internacia.database.duckdb") as mock_duckdb:
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_conn
            mock_conn.execute.return_value.description = [("code",)]
            mock_conn.execute.return_value.fetchall.return_value = [("US",)]
            mock_duckdb.connect.return_value = mock_conn

            manager = DatabaseManager(mock_db_path)
            result = manager.execute_query_dict(
                "SELECT code FROM countries WHERE code = ?", ("US",)
            )

            assert len(result) == 1
            assert result[0]["code"] == "US"
            mock_conn.execute.assert_called_once_with(
                "SELECT code FROM countries WHERE code = ?", ("US",)
            )

    def test_execute_query_dict_error_handling(self, mock_db_path):
        """Test execute_query_dict error handling."""
        with patch("internacia.database.duckdb") as mock_duckdb:
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_conn
            mock_conn.execute.side_effect = Exception("SQL syntax error")
            mock_duckdb.connect.return_value = mock_conn

            manager = DatabaseManager(mock_db_path)

            with pytest.raises(DatabaseError) as exc_info:
                manager.execute_query_dict("INVALID SQL")

            assert "Query execution failed" in str(exc_info.value)
            mock_conn.close.assert_called_once()

    def test_execute_query_dict_empty_result(self, mock_db_path):
        """Test execute_query_dict with empty result."""
        with patch("internacia.database.duckdb") as mock_duckdb:
            mock_conn = MagicMock()
            mock_conn.cursor.return_value = mock_conn
            mock_conn.execute.return_value.description = [("code",)]
            mock_conn.execute.return_value.fetchall.return_value = []
            mock_duckdb.connect.return_value = mock_conn

            manager = DatabaseManager(mock_db_path)
            result = manager.execute_query_dict("SELECT * FROM countries WHERE code = 'XX'")

            assert not result


class TestDatabaseManagerConnection:
    """One read-only connection per manager, one cursor per query."""

    def test_connection_is_opened_once_read_only(self, mock_db_path):
        with patch("internacia.database.duckdb") as mock_duckdb:
            mock_conn = MagicMock()
            mock_duckdb.connect.return_value = mock_conn
            manager = DatabaseManager(mock_db_path)
            manager.execute_query("SELECT 1")
            manager.execute_query("SELECT 2")
            mock_duckdb.connect.assert_called_once_with(str(mock_db_path), read_only=True)
            assert mock_conn.cursor.call_count == 2
            assert mock_conn.cursor.return_value.close.call_count == 2
            mock_conn.close.assert_not_called()

    def test_cursor_closed_on_exception(self, mock_db_path):
        with patch("internacia.database.duckdb") as mock_duckdb:
            mock_conn = MagicMock()
            mock_conn.cursor.return_value.execute.side_effect = Exception("Test error")
            mock_duckdb.connect.return_value = mock_conn
            manager = DatabaseManager(mock_db_path)
            with pytest.raises(DatabaseError):
                manager.execute_query("SELECT * FROM test")
            mock_conn.cursor.return_value.close.assert_called_once()

    def test_close_and_reopen(self, mock_db_path):
        with patch("internacia.database.duckdb") as mock_duckdb:
            manager = DatabaseManager(mock_db_path)
            manager.execute_query("SELECT 1")
            manager.close()
            mock_duckdb.connect.return_value.close.assert_called_once()
            manager.execute_query("SELECT 1")
            assert mock_duckdb.connect.call_count == 2

    def test_connection_failure_is_a_database_error(self, mock_db_path):
        with patch("internacia.database.duckdb") as mock_duckdb:
            mock_duckdb.connect.side_effect = Exception("Connection failed")
            manager = DatabaseManager(mock_db_path)
            with pytest.raises(DatabaseError, match="Connection failed"):
                manager.execute_query("SELECT 1")

    def test_real_connection_is_shared_across_threads(self, mock_db_path):
        from concurrent.futures import ThreadPoolExecutor

        manager = DatabaseManager(mock_db_path)
        with ThreadPoolExecutor(max_workers=8) as pool:
            counts = list(
                pool.map(lambda _: manager.execute_query("SELECT count(*) FROM _meta"), range(32))
            )
        assert {c[0][0] for c in counts} == {2}
