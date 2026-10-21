"""Every public client method against a real internacia-db release."""

import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import duckdb
import pytest

from internacia import DatabaseError, InternaciaClient

PLAIN_TYPES = (str, int, float, bool, type(None))


def assert_plain(value: Any, path: str = "result") -> None:
    """Fail if anything other than dict/list/str/int/float/bool/None is returned."""
    if isinstance(value, dict):
        for key, item in value.items():
            assert isinstance(key, str), f"{path}: non-string key {key!r}"
            assert_plain(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            assert_plain(item, f"{path}[{index}]")
    else:
        assert isinstance(value, PLAIN_TYPES), f"{path}: {type(value).__module__}.{type(value)}"


PUBLIC_CALLS: dict[str, Callable[[InternaciaClient], Any]] = {
    "countries.get_by_code": lambda c: c.countries.get_by_code("US"),
    "countries.get_by_iso3": lambda c: c.countries.get_by_iso3("FRA"),
    "countries.get_by_numeric_code": lambda c: c.countries.get_by_numeric_code("840"),
    "countries.get_all": lambda c: c.countries.get_all(),
    "countries.get_all_limit": lambda c: c.countries.get_all(limit=5),
    "countries.get_by_region": lambda c: c.countries.get_by_region("NAC"),
    "countries.get_by_income_level": lambda c: c.countries.get_by_income_level("OEC"),
    "countries.get_un_members": lambda c: c.countries.get_un_members(),
    "countries.get_independent": lambda c: c.countries.get_independent(),
    "countries.get_by_continent": lambda c: c.countries.get_by_continent("Europe"),
    "countries.get_by_currency": lambda c: c.countries.get_by_currency("EUR"),
    "countries.get_by_language": lambda c: c.countries.get_by_language("fra"),
    "countries.count": lambda c: c.countries.count(),
    "intblocks.get_by_id": lambda c: c.intblocks.get_by_id("EU"),
    "intblocks.get_all": lambda c: c.intblocks.get_all(),
    "intblocks.get_all_limit": lambda c: c.intblocks.get_all(limit=5),
    "intblocks.get_by_blocktype": lambda c: c.intblocks.get_by_blocktype("economic"),
    "intblocks.get_by_status": lambda c: c.intblocks.get_by_status("formal"),
    "intblocks.get_by_geographic_scope": lambda c: c.intblocks.get_by_geographic_scope("regional"),
    "intblocks.get_by_member": lambda c: c.intblocks.get_by_member("FR"),
    "intblocks.get_by_acronym": lambda c: c.intblocks.get_by_acronym("NATO"),
    "intblocks.get_by_tag": lambda c: c.intblocks.get_by_tag("trade"),
    "intblocks.get_by_topic": lambda c: c.intblocks.get_by_topic("trade"),
    "intblocks.get_by_founded_year": lambda c: c.intblocks.get_by_founded_year(1945),
    "intblocks.count": lambda c: c.intblocks.count(),
    "search.fuzzy": lambda c: c.search.fuzzy("United States"),
    "search.search_countries": lambda c: c.search.search_countries("Germany"),
    "search.search_intblocks": lambda c: c.search.search_intblocks("NATO"),
}


@pytest.mark.parametrize("name", sorted(PUBLIC_CALLS))
def test_public_call_returns_plain_json_data(client: InternaciaClient, name: str) -> None:
    result = PUBLIC_CALLS[name](client)

    assert result, f"{name} returned an empty result"
    assert_plain(result)
    json.dumps(result)


def test_meta_version_matches_pin(real_db_path: Path, expected_db_version: str | None) -> None:
    if not expected_db_version:
        pytest.skip("INTERNACIA_TEST_DB_VERSION is not set")
    conn = duckdb.connect(str(real_db_path), read_only=True)
    try:
        versions = {row[0] for row in conn.execute("SELECT version FROM _meta").fetchall()}
    finally:
        conn.close()
    assert versions == {expected_db_version}


def codes(rows: list[Any], key: str = "code") -> set[str]:
    return {row[key] for row in rows}


def test_get_by_currency(client: InternaciaClient) -> None:
    eur = codes(client.countries.get_by_currency("eur"))
    assert {"DE", "FR", "IT", "ES"} <= eur
    assert "US" not in eur


def test_get_by_language(client: InternaciaClient) -> None:
    assert {"FR", "BE", "CA"} <= codes(client.countries.get_by_language("FRA"))


def test_get_by_member(client: InternaciaClient) -> None:
    blocks = client.intblocks.get_by_member("fr")
    assert {"EU", "NATO", "UN"} <= codes(blocks, "id")
    assert len(blocks) == len(codes(blocks, "id")), "duplicate blocks returned"


def test_get_by_acronym_matches_case_insensitively(client: InternaciaClient) -> None:
    assert "NATO" in codes(client.intblocks.get_by_acronym("nato"), "id")


def test_get_by_topic(client: InternaciaClient) -> None:
    blocks = client.intblocks.get_by_topic("trade")
    assert all(any(t["key"] == "trade" for t in b["topics"]) for b in blocks)


def test_nullable_nested_lists_are_none(client: InternaciaClient) -> None:
    countries = client.countries.get_all()
    without_currencies = [c for c in countries if c["currencies"] is None]
    without_languages = [c for c in countries if c["languages"] is None]

    assert without_currencies, "expected some countries with NULL currencies"
    assert without_languages, "expected some countries with NULL languages"
    json.dumps(without_currencies + without_languages)


@pytest.mark.parametrize(
    ("query", "code"),
    [("Deutschland", "DE"), ("Россия", "RU"), ("Allemagne", "DE"), ("俄罗斯", "RU")],
)
def test_search_countries_by_native_name(client: InternaciaClient, query: str, code: str) -> None:
    assert code in codes(client.search.search_countries(query))


@pytest.mark.parametrize(
    "query", ["Европейский союз", "欧盟", "Union européenne", "Europäische Union", "ЕС"]
)
def test_search_intblocks_multilingual(client: InternaciaClient, query: str) -> None:
    assert "EU" in codes(client.search.search_intblocks(query, limit=20), "id")


def test_fuzzy_exact_code_ranks_first(client: InternaciaClient) -> None:
    results = client.search.fuzzy("DE")
    assert results[0]["type"] == "country"
    assert results[0]["code"] == "DE"


def test_scope_category_values_are_open_strings(client: InternaciaClient) -> None:
    values = {b.get("scope_category") for b in client.intblocks.get_all()}
    assert all(v is None or isinstance(v, str) for v in values)
    assert len(values - {None}) >= 2


def test_unknown_scope_category_is_returned_unchanged(derived_db: Callable[..., Path]) -> None:
    path = derived_db(
        "SELECT * FROM src.countries LIMIT 0",
        "SELECT * REPLACE ('category_from_the_future' AS scope_category) "
        "FROM src.intblocks WHERE id = 'EU'",
    )
    block = InternaciaClient(db_path=path).intblocks.get_by_id("EU")

    assert block is not None
    assert block["scope_category"] == "category_from_the_future"


def test_search_query_failure_raises(derived_db: Callable[..., Path]) -> None:
    path = derived_db(
        "SELECT * EXCLUDE (native_names) FROM src.countries",
        "SELECT * FROM src.intblocks",
    )
    with pytest.raises(DatabaseError):
        InternaciaClient(db_path=path).search.search_countries("Deutschland")
