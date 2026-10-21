"""Fixtures for integration tests against a real internacia-db DuckDB file.

Set ``INTERNACIA_TEST_DB_PATH`` to a release ``internacia.duckdb`` (see
``scripts/fetch_test_db.py``). Without it the integration tests are skipped.
``INTERNACIA_TEST_DB_VERSION``, when set, must match ``_meta.version``.
"""

import os
from collections.abc import Callable
from pathlib import Path

import duckdb
import pytest

from internacia import InternaciaClient

ENV_DB_PATH = "INTERNACIA_TEST_DB_PATH"
ENV_DB_VERSION = "INTERNACIA_TEST_DB_VERSION"


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    here = Path(__file__).parent
    for item in items:
        if here in Path(item.fspath).parents:
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def real_db_path() -> Path:
    value = os.getenv(ENV_DB_PATH)
    if not value:
        if os.getenv("CI"):
            pytest.fail(f"{ENV_DB_PATH} must be set in CI")
        pytest.skip(f"{ENV_DB_PATH} is not set")
    path = Path(value)
    if not path.is_file():
        pytest.fail(f"{ENV_DB_PATH}={value} does not exist")
    return path


@pytest.fixture(scope="session")
def expected_db_version() -> str | None:
    return os.getenv(ENV_DB_VERSION)


@pytest.fixture(scope="session")
def client(real_db_path: Path) -> InternaciaClient:
    return InternaciaClient(db_path=real_db_path)


@pytest.fixture
def derived_db(real_db_path: Path, tmp_path: Path) -> Callable[[str, str], Path]:
    """Build a small DuckDB file from SQL over the real one, attached as ``src``."""

    def build(countries_sql: str, intblocks_sql: str) -> Path:
        path = tmp_path / "derived.duckdb"
        conn = duckdb.connect(str(path))
        try:
            conn.execute(f"ATTACH '{real_db_path.as_posix()}' AS src (READ_ONLY)")
            conn.execute(f"CREATE TABLE countries AS {countries_sql}")
            conn.execute(f"CREATE TABLE intblocks AS {intblocks_sql}")
            conn.execute("CREATE TABLE _meta AS SELECT * FROM src._meta")
        finally:
            conn.close()
        return path

    return build
