"""DuckDB connection manager for internacia SDK: one read-only connection per client."""

import logging
import threading
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import duckdb

from internacia.exceptions import DatabaseError

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Holds one read-only DuckDB connection, opened on first use.

    Each query runs on its own cursor (``connection.cursor()``), which DuckDB documents as
    the way to use one database from several threads.
    """

    def __init__(self, db_path: Path):
        """
        Initialize the database manager.

        Args:
            db_path: Path to the DuckDB database file

        Raises:
            DatabaseError: If the database file doesn't exist
        """
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            logger.error("Database file not found: %s", self.db_path)
            raise DatabaseError(
                f"Database file not found: {self.db_path}. "
                "Please ensure the internacia-db dataset has been built."
            )
        self._connection: duckdb.DuckDBPyConnection | None = None
        self._lock = threading.Lock()
        self._relations: set[str] | None = None
        logger.debug("DatabaseManager initialized with path: %s", self.db_path)

    def _connect(self) -> duckdb.DuckDBPyConnection:
        with self._lock:
            if self._connection is None:
                logger.debug("Opening read-only connection to %s", self.db_path)
                self._connection = duckdb.connect(str(self.db_path), read_only=True)
            return self._connection

    @contextmanager
    def get_connection(self) -> Generator[duckdb.DuckDBPyConnection, None, None]:
        """
        Yield a cursor on the shared read-only connection; the cursor is closed afterwards.

        Example:
            >>> with db_manager.get_connection() as conn:
            ...     result = conn.execute("SELECT * FROM countries LIMIT 1").fetchall()
        """
        cursor = self._connect().cursor()
        try:
            yield cursor
        finally:
            cursor.close()

    def close(self) -> None:
        """Close the shared connection; the next query opens a new one."""
        with self._lock:
            if self._connection is not None:
                self._connection.close()
                self._connection = None

    def has_relation(self, name: str) -> bool:
        """Whether a table or view called ``name`` exists (cached per manager)."""
        if self._relations is None:
            rows = self.execute_query(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'main'"
            )
            self._relations = {row[0] for row in rows}
        return name in self._relations

    def execute_query(self, query: str, parameters: tuple | dict | None = None) -> list:
        """
        Execute a query and return results as a list of tuples.

        Args:
            query: SQL query string
            parameters: Query parameters (optional)

        Returns:
            List of result rows (tuples)

        Raises:
            DatabaseError: If the query execution fails
        """
        try:
            query_preview = query[:100] + "..." if len(query) > 100 else query
            logger.debug("Executing query: %s", query_preview)
            with self.get_connection() as conn:
                if parameters:
                    result = conn.execute(query, parameters).fetchall()
                else:
                    result = conn.execute(query).fetchall()
                logger.debug("Query returned %s rows", len(result))
                return result
        except Exception as e:
            logger.error("Query execution failed: %s", str(e))
            raise DatabaseError(f"Query execution failed: {str(e)}") from e

    def execute_query_dict(
        self, query: str, parameters: tuple | dict | None = None
    ) -> list[dict[str, Any]]:
        """
        Execute a query and return results as a list of dictionaries.

        Args:
            query: SQL query string
            parameters: Query parameters (optional)

        Returns:
            List of result rows (dictionaries with column names as keys).
            Values are plain Python types: LIST columns become ``list``,
            STRUCT and MAP columns become ``dict`` and SQL NULL becomes ``None``.

        Raises:
            DatabaseError: If the query execution fails
        """
        try:
            query_preview = query[:100] + "..." if len(query) > 100 else query
            logger.debug("Executing query: %s", query_preview)
            with self.get_connection() as conn:
                if parameters:
                    cursor = conn.execute(query, parameters)
                else:
                    cursor = conn.execute(query)
                columns = [col[0] for col in cursor.description]
                records = [dict(zip(columns, row, strict=True)) for row in cursor.fetchall()]
                logger.debug("Query returned %s rows", len(records))
                return records
        except Exception as e:
            logger.error("Query execution failed: %s", str(e))
            raise DatabaseError(f"Query execution failed: {str(e)}") from e
