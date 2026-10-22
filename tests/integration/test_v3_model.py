"""Memberships, blocktypes, id resolution and derived catalogs on a real database."""

from collections.abc import Callable
from pathlib import Path

import duckdb

from internacia import InternaciaClient


def test_current_memberships(client: InternaciaClient) -> None:
    nato = client.memberships.get_by_intblock("nato")
    assert {"US", "FR", "TR"} <= {m["country_code"] for m in nato}
    assert all(m["status"] != "former_member" and m["left"] is None for m in nato)
    us_all = client.memberships.get_by_country("US", current_only=False)
    us_current = client.memberships.get_by_country("US")
    former = {m["intblock_id"] for m in us_all if m["status"] == "former_member"}
    assert former and not former & {m["intblock_id"] for m in us_current}
    assert client.memberships.is_member("US", "NATO")
    assert not client.memberships.is_member("US", "NAFTA")
    assert client.memberships.is_member("US", "NAFTA", current_only=False)


def test_get_by_member_current_only(client: InternaciaClient) -> None:
    every = {b["id"] for b in client.intblocks.get_by_member("US")}
    current = {b["id"] for b in client.intblocks.get_by_member("US", current_only=True)}
    assert "NATO" in current and "NAFTA" in every - current


def test_blocktypes(client: InternaciaClient) -> None:
    types = client.blocktypes.get_all()
    assert len(types) >= 70
    assert client.blocktypes.get_by_id("Economic")["id"] == "economic"
    assert client.blocktypes.get_by_id("no-such-type") is None


def test_catalogs_are_null_safe(client: InternaciaClient) -> None:
    eur = client.countries.get_currency("eur")
    assert eur and eur["country_count"] >= 20
    assert client.countries.get_country_currencies("CH") == [
        {"code": "CHF", "name": "Swiss franc", "symbol": "Fr."}
    ]
    assert client.countries.get_country_currencies("AQ") == []
    assert client.countries.get_language("FRA")["country_count"] >= 20
    assert client.countries.get_country_languages("AQ") == []
    assert len(client.countries.get_country_timezones("RU")) > 5
    assert "FR" in {c["code"] for c in client.countries.get_by_timezone("Europe/Paris")}
    assert client.countries.get_region("ecs")["country_count"] > 40
    assert {t["timezone"] for t in client.countries.get_timezones()} >= {"Europe/Paris"}


def test_resolution_without_alias_tables(client: InternaciaClient) -> None:
    assert client.intblocks.resolve_id("eu")["status"] == "current"
    assert client.intblocks.resolve_id("NO-SUCH-ID") == {
        "input": "NO-SUCH-ID",
        "id": None,
        "status": "unknown",
        "since": None,
        "note": None,
        "disambiguated": None,
    }


def test_resolution_with_alias_tables(real_db_path: Path, tmp_path: Path) -> None:
    path = tmp_path / "with_aliases.duckdb"
    con = duckdb.connect(str(path))
    try:
        con.execute(f"ATTACH '{real_db_path.as_posix()}' AS src (READ_ONLY)")
        for table in ("countries", "intblocks", "_meta"):
            con.execute(f"CREATE TABLE {table} AS SELECT * FROM src.{table}")
        con.execute(
            "CREATE TABLE intblocks_aliases AS SELECT * FROM (VALUES "
            "('USAN', 'UNASUR', 'merged', '3.0.0', 'dup'), "
            "('ASF', 'FSA', 'disambiguated', '1.3.0', ''), "
            "('GONE1', '', 'retired', '3.1.0', '')) AS t(alias, target, reason, since, note)"
        )
        con.execute(
            "CREATE TABLE countries_aliases AS SELECT 'KV' AS alias, 'XK' AS target, "
            "'renamed' AS reason, '1.11.0' AS since, '' AS note"
        )
    finally:
        con.close()
    with InternaciaClient(db_path=path) as client:
        usan = client.intblocks.resolve_id("usan")
        assert (usan["id"], usan["status"], usan["since"]) == ("UNASUR", "merged", "3.0.0")
        asf = client.intblocks.resolve_id("ASF")
        assert (asf["id"], asf["status"], asf["disambiguated"]) == ("ASF", "current", "FSA")
        assert client.intblocks.resolve_id("GONE1")["id"] is None
        assert client.intblocks.resolve_id("GONE1")["status"] == "retired"
        assert client.countries.resolve_code("kv")["id"] == "XK"


def test_views_are_used_when_present(derived_db: Callable[..., Path]) -> None:
    path = derived_db("SELECT * FROM src.countries", "SELECT * FROM src.intblocks")
    con = duckdb.connect(str(path))
    try:
        con.execute(
            "CREATE VIEW country_timezones AS SELECT 'ZZ' AS country_code, 'Etc/Test' AS timezone"
        )
    finally:
        con.close()
    with InternaciaClient(db_path=path) as client:
        assert client.countries.get_timezones() == [{"timezone": "Etc/Test", "country_count": 1}]


def test_client_is_a_context_manager(real_db_path: Path) -> None:
    with InternaciaClient(db_path=real_db_path) as client:
        assert client.countries.count() > 0
    assert client.countries.count() > 0  # reopens after close
