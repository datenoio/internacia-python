"""What internacia-db must keep working for this SDK.

Every public method is called with facts that are stable across releases (country codes,
long-standing organizations). A failure here means a database change broke the SDK.
"""

import datetime
from collections.abc import Callable
from decimal import Decimal
from typing import Any

import pytest

from internacia import SUPPORTED_CONTRACT_MAJOR, InternaciaClient

PLAIN = (str, int, float, bool, type(None), datetime.date, datetime.datetime, Decimal)


def assert_plain(value: Any, path: str = "result") -> None:
    """Results contain only plain Python types (no numpy, pandas or Arrow objects)."""
    if isinstance(value, dict):
        for key, item in value.items():
            assert isinstance(key, str), f"{path}: non-string key {key!r}"
            assert_plain(item, f"{path}.{key}")
    elif isinstance(value, list):
        for i, item in enumerate(value):
            assert_plain(item, f"{path}[{i}]")
    else:
        assert isinstance(value, PLAIN), f"{path}: {type(value).__module__}.{type(value).__name__}"


def test_meta_and_contract(client: InternaciaClient) -> None:
    meta = client.meta()
    assert int(meta["contract_version"].split(".")[0]) == SUPPORTED_CONTRACT_MAJOR
    assert meta["version"].split(".")[0] == str(SUPPORTED_CONTRACT_MAJOR)
    for dataset in ("countries", "intblocks", "blocktypes", "memberships"):
        assert meta["datasets"][dataset]["row_count"] > 0
        assert meta["datasets"][dataset]["schema_hash"]


SINGLE: list[tuple[str, Callable[[InternaciaClient], Any], dict[str, Any]]] = [
    (
        "countries.get_by_code",
        lambda c: c.countries.get_by_code("FR"),
        {"code": "FR", "iso3code": "FRA"},
    ),
    ("countries.get_by_iso3", lambda c: c.countries.get_by_iso3("FRA"), {"code": "FR"}),
    (
        "countries.get_by_numeric_code",
        lambda c: c.countries.get_by_numeric_code("250"),
        {"code": "FR"},
    ),
    ("intblocks.get_by_id", lambda c: c.intblocks.get_by_id("EU"), {"id": "EU"}),
]


@pytest.mark.parametrize(("name", "call", "expected"), SINGLE, ids=[s[0] for s in SINGLE])
def test_lookups(client: InternaciaClient, name: str, call: Callable, expected: dict) -> None:
    record = call(client)
    assert record is not None, name
    for key, value in expected.items():
        assert record[key] == value
    assert_plain(record)


LISTS: list[tuple[str, Callable[[InternaciaClient], list], str, str]] = [
    ("countries.get_all", lambda c: c.countries.get_all(limit=5), "code", ""),
    ("countries.get_by_region", lambda c: c.countries.get_by_region("ECS"), "code", "FR"),
    (
        "countries.get_by_income_level",
        lambda c: c.countries.get_by_income_level("LMC"),
        "code",
        "IN",
    ),
    ("countries.get_un_members", lambda c: c.countries.get_un_members(), "code", "FR"),
    ("countries.get_independent", lambda c: c.countries.get_independent(), "code", "FR"),
    ("countries.get_by_continent", lambda c: c.countries.get_by_continent("Europe"), "code", "FR"),
    ("countries.get_by_currency", lambda c: c.countries.get_by_currency("EUR"), "code", "FR"),
    ("countries.get_by_language", lambda c: c.countries.get_by_language("fra"), "code", "FR"),
    ("intblocks.get_all", lambda c: c.intblocks.get_all(limit=5), "id", ""),
    ("intblocks.get_by_blocktype", lambda c: c.intblocks.get_by_blocktype("economic"), "id", "EU"),
    ("intblocks.get_by_status", lambda c: c.intblocks.get_by_status("formal"), "id", "EU"),
    (
        "intblocks.get_by_geographic_scope",
        lambda c: c.intblocks.get_by_geographic_scope("regional"),
        "id",
        "EU",
    ),
    ("intblocks.get_by_member", lambda c: c.intblocks.get_by_member("FR"), "id", "EU"),
    ("intblocks.get_by_acronym", lambda c: c.intblocks.get_by_acronym("NATO"), "id", "NATO"),
    ("intblocks.get_by_tag", lambda c: c.intblocks.get_by_tag("trade"), "id", ""),
    ("intblocks.get_by_topic", lambda c: c.intblocks.get_by_topic("economy"), "id", ""),
    ("intblocks.get_by_founded_year", lambda c: c.intblocks.get_by_founded_year(1945), "id", ""),
    ("search.fuzzy", lambda c: c.search.fuzzy("France"), "", ""),
    ("search.search_countries", lambda c: c.search.search_countries("Germany"), "code", "DE"),
    ("search.search_intblocks", lambda c: c.search.search_intblocks("NATO"), "id", "NATO"),
]


@pytest.mark.parametrize(("name", "call", "key", "contains"), LISTS, ids=[s[0] for s in LISTS])
def test_list_methods(
    client: InternaciaClient, name: str, call: Callable, key: str, contains: str
) -> None:
    rows = call(client)
    assert rows, f"{name} returned no rows"
    if contains:
        assert contains in {row.get(key) for row in rows}, f"{name} lacks {contains}"
    assert_plain(rows)


def test_counts(client: InternaciaClient) -> None:
    assert client.countries.count() >= 249
    assert client.intblocks.count() >= 1000


def test_unknown_open_enum_values_are_accepted(client: InternaciaClient) -> None:
    """Enum-like filters take open strings: unknown values return nothing, not an error."""
    assert client.intblocks.get_by_status("not-a-status-yet") == []
    assert client.intblocks.get_by_geographic_scope("not-a-scope-yet") == []
    assert client.intblocks.get_by_blocktype("not-a-blocktype-yet") == []
