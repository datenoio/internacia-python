"""Fixtures for the portable data-contract suite.

internacia-db runs this suite against a freshly built database before every release
(set ``INTERNACIA_CONTRACT_DB_PATH``). In this repository it falls back to the release
file used by the integration tests (``INTERNACIA_TEST_DB_PATH``).
"""

import os
from pathlib import Path

import pytest

from internacia import InternaciaClient

ENV_VARS = ("INTERNACIA_CONTRACT_DB_PATH", "INTERNACIA_TEST_DB_PATH")


def pytest_collection_modifyitems(items: list[pytest.Item]) -> None:
    here = Path(__file__).parent
    for item in items:
        if here in Path(item.fspath).parents:
            item.add_marker(pytest.mark.contract)


@pytest.fixture(scope="session")
def contract_db_path() -> Path:
    value = next((os.environ[name] for name in ENV_VARS if os.getenv(name)), None)
    if not value:
        if os.getenv("CI"):
            pytest.fail(f"one of {', '.join(ENV_VARS)} must be set in CI")
        pytest.skip(f"none of {', '.join(ENV_VARS)} is set")
    path = Path(value)
    if not path.is_file():
        pytest.fail(f"{value} does not exist")
    return path


@pytest.fixture(scope="session")
def client(contract_db_path: Path) -> InternaciaClient:
    return InternaciaClient(db_path=contract_db_path)
