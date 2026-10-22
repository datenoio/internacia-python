"""Main client class for Internacia SDK."""

import logging
import os
from pathlib import Path
from typing import Any

from internacia import contract
from internacia.config import Config
from internacia.countries import CountriesClient
from internacia.database import DatabaseManager
from internacia.exceptions import ContractError, DatabaseError
from internacia.intblocks import IntblocksClient
from internacia.search import SearchClient

logger = logging.getLogger(__name__)


class InternaciaClient:
    """
    Main client for accessing internacia-db data.

    This client provides access to countries, international blocks, and search
    functionality through a unified interface.

    Example:
        >>> from internacia import InternaciaClient
        >>> client = InternaciaClient()
        >>> country = client.countries.get_by_code("US")
        >>> results = client.search.fuzzy("United States")
    """

    def __init__(
        self,
        db_path: Path | None = None,
        data_dir: Path | None = None,  # pylint: disable=unused-argument
        data_version: str | None = None,
        check_contract: bool = True,
    ):
        """
        Initialize the Internacia client.

        Args:
            db_path: Path to the DuckDB database file. If None, uses
                ``INTERNACIA_DB_PATH`` or a database downloaded with ``download_database``.
            data_dir: Unused; kept for backward compatibility.
            data_version: Use this cached release (e.g. ``"3.1.0"``) instead of the newest
                cached one. Defaults to ``INTERNACIA_DATA_VERSION``.
            check_contract: Verify that the database's data contract is supported.

        Raises:
            FileNotFoundError: If the database file cannot be found
            ContractError: If the database's contract major is not supported
        """
        Config.setup_logging()

        if db_path is None:
            db_path = Config.get_db_path(data_version=data_version)
            if db_path is None:
                pinned = data_version or os.getenv(Config.ENV_DATA_VERSION)
                raise FileNotFoundError(
                    "Could not find internacia.duckdb"
                    + (f" for data version {pinned}" if pinned else "")
                    + ". Pass db_path, set INTERNACIA_DB_PATH, or download it:\n"
                    "  from internacia import download_database\n"
                    + (f"  download_database({pinned!r})" if pinned else "  download_database()")
                )
            if not db_path.exists():
                raise FileNotFoundError(f"Database file not found at: {db_path}")
        else:
            db_path = Path(db_path)
            if not db_path.exists():
                raise FileNotFoundError(f"Database file not found at specified path: {db_path}")

        logger.info("Initializing InternaciaClient with database: %s", db_path)
        self._db_manager = DatabaseManager(db_path)
        self._meta: dict[str, Any] | None = None
        if check_contract:
            contract.check_contract(self.meta())
        self.countries = CountriesClient(self._db_manager)
        self.intblocks = IntblocksClient(self._db_manager)
        self.search = SearchClient(self._db_manager)

    def meta(self) -> dict[str, Any]:
        """
        Version and build information from the database's ``_meta`` table.

        Returns:
            ``version``, ``contract_version``, ``build_date``, ``git_commit``,
            ``data_license`` and ``datasets`` (``{name: {"row_count", "schema_hash"}}``).
            Databases built before ``contract_version`` existed (internacia-db 3.0.0)
            report ``MAJOR.MINOR`` of their version.

        Raises:
            ContractError: If the database has no ``_meta`` table
        """
        if self._meta is None:
            try:
                rows = self._db_manager.execute_query_dict("SELECT * FROM _meta ORDER BY dataset")
            except DatabaseError as e:
                raise ContractError(
                    f"{self._db_manager.db_path} has no readable _meta table: {e}"
                ) from e
            if not rows:
                raise ContractError(f"{self._db_manager.db_path} has an empty _meta table")
            first = rows[0]
            version = str(first.get("version"))
            major, minor = contract.parse_contract(first.get("contract_version") or version)
            self._meta = {
                "version": version,
                "contract_version": f"{major}.{minor}",
                "build_date": first.get("build_date"),
                "git_commit": first.get("git_commit"),
                "data_license": first.get("data_license"),
                "datasets": {
                    row["dataset"]: {
                        "row_count": row.get("row_count"),
                        "schema_hash": row.get("schema_hash"),
                    }
                    for row in rows
                },
            }
        return {**self._meta, "datasets": {k: dict(v) for k, v in self._meta["datasets"].items()}}
