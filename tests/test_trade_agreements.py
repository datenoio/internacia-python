"""Trade agreements registry and ids moved to it (internacia-db contract 5)."""

import duckdb
import pytest

from internacia import InternaciaClient
from internacia.tools import call_tool
from tests.conftest import make_meta_db


@pytest.fixture
def v5_db(tmp_path):
    """A contract 5.0 database: CETA moved out of intblocks, USCR merged into CAFTADR."""
    path = make_meta_db(tmp_path / "v5.duckdb", version="5.0.0", contract_version="5.0")
    con = duckdb.connect(str(path))
    try:
        con.execute(
            "CREATE TABLE intblocks AS SELECT * FROM (VALUES ('EU', 'European Union'), "
            "('CAFTADR', 'CAFTA-DR')) AS t(id, name)"
        )
        con.execute(
            "CREATE TABLE intblocks_aliases AS SELECT * FROM (VALUES "
            "('CETA', 'CETA', 'moved', '5.0.0', 'Two-party FTA', 'trade_agreements'), "
            "('USCR', 'CAFTADR', 'merged', '5.0.0', '', 'intblocks'), "
            "('GONE1', NULL, 'retired', '3.1.0', '', NULL)"
            ") AS t(alias, target, reason, since, note, target_dataset)"
        )
        con.execute(
            "CREATE TABLE trade_agreements AS SELECT * FROM (VALUES "
            "('CETA', 'Comprehensive Economic and Trade Agreement', 'fta', 'in_force', "
            "'2017-09-21', NULL, 2), "
            "('CAFTADR', 'CAFTA-DR', 'fta', 'in_force', '2006-03-01', 'CAFTADR', 7)"
            ") AS t(id, name, agreement_type, status, in_force, intblock_id, party_count)"
        )
        con.execute(
            "CREATE TABLE trade_agreement_parties AS SELECT * FROM (VALUES "
            "('CETA', 'EU', 'intblock', 'party', NULL), "
            "('CETA', 'CA', 'country', 'party', NULL), "
            "('CETA', 'GB', 'country', 'former_party', '2020-12-31')"
            ') AS t(agreement_id, party_id, party_type, status, "left")'
        )
        con.execute(
            "CREATE VIEW country_trade_agreements AS SELECT * FROM (VALUES "
            "('FR', 'CETA', 'EU', 'fta', 'in_force', '2017-09-21'), "
            "('CA', 'CETA', NULL, 'fta', 'in_force', '2017-09-21')"
            ") AS t(country_code, agreement_id, via, agreement_type, agreement_status, in_force)"
        )
    finally:
        con.close()
    return path


@pytest.fixture
def v4_db(tmp_path):
    """A contract 4.4 database: CETA is an intblock, aliases have no target_dataset."""
    path = make_meta_db(tmp_path / "v4.duckdb", version="4.4.0", contract_version="4.4")
    con = duckdb.connect(str(path))
    try:
        con.execute(
            "CREATE TABLE intblocks AS SELECT * FROM (VALUES ('EU', 'European Union'), "
            "('CETA', 'CETA')) AS t(id, name)"
        )
        con.execute(
            "CREATE TABLE intblocks_aliases AS SELECT 'USAN' AS alias, 'UNASUR' AS target, "
            "'merged' AS reason, '3.0.0' AS since, '' AS note"
        )
    finally:
        con.close()
    return path


def test_moved_alias_reports_target_dataset(v5_db):
    with InternaciaClient(db_path=v5_db) as client:
        assert client.intblocks.resolve_id("ceta") == {
            "input": "CETA",
            "id": "CETA",
            "status": "moved",
            "since": "5.0.0",
            "note": "Two-party FTA",
            "disambiguated": None,
            "target_dataset": "trade_agreements",
        }
        assert client.intblocks.get_by_id("CETA") is None
        merged = client.intblocks.resolve_id("USCR")
        assert (merged["id"], merged["status"], merged["target_dataset"]) == (
            "CAFTADR",
            "merged",
            "intblocks",
        )
        retired = client.intblocks.resolve_id("GONE1")
        assert (retired["id"], retired["status"], retired["target_dataset"]) == (
            None,
            "retired",
            None,
        )
        assert client.intblocks.resolve_id("EU")["target_dataset"] == "intblocks"
        assert client.intblocks.resolve_id("NOPE")["target_dataset"] is None


def test_aliases_without_target_dataset_column(v4_db):
    """Contract 3.x/4.x alias tables point into the table they belong to."""
    with InternaciaClient(db_path=v4_db) as client:
        usan = client.intblocks.resolve_id("USAN")
        assert (usan["id"], usan["status"], usan["target_dataset"]) == (
            "UNASUR",
            "merged",
            "intblocks",
        )
        ceta = client.intblocks.resolve_id("CETA")
        assert (ceta["status"], ceta["target_dataset"]) == ("current", "intblocks")


def test_trade_agreements_accessor(v5_db):
    with InternaciaClient(db_path=v5_db) as client:
        ceta = client.trade_agreements.get_by_id("ceta")
        assert ceta is not None and (ceta["agreement_type"], ceta["party_count"]) == ("fta", 2)
        assert client.trade_agreements.get_by_id("NOPE") is None
        parties = client.trade_agreements.get_parties("ceta")
        assert [p["party_id"] for p in parties] == ["CA", "EU", "GB"]
        current = client.trade_agreements.get_parties("CETA", current_only=True)
        assert [p["party_id"] for p in current] == ["CA", "EU"]
        assert client.trade_agreements.get_by_country("fr") == [
            {
                "country_code": "FR",
                "agreement_id": "CETA",
                "via": "EU",
                "agreement_type": "fta",
                "agreement_status": "in_force",
                "in_force": "2017-09-21",
            }
        ]
        assert client.trade_agreements.get_by_country("ZZ") == []


def test_trade_agreements_on_databases_without_the_registry(v4_db):
    with InternaciaClient(db_path=v4_db) as client:
        assert client.trade_agreements.get_by_id("CETA") is None
        assert client.trade_agreements.get_parties("CETA") == []
        assert client.trade_agreements.get_by_country("FR") == []


def test_intblock_lookup_follows_moved_ids(v5_db, v4_db):
    with InternaciaClient(db_path=v5_db) as client:
        ceta = call_tool(client, "intblock_lookup", {"id": "CETA"})
        assert (ceta["id"], ceta["agreement_type"]) == ("CETA", "fta")
        assert call_tool(client, "intblock_lookup", {"id": "USCR"})["id"] == "CAFTADR"
        assert call_tool(client, "intblock_lookup", {"id": "GONE1"}) is None
        assert call_tool(client, "trade_agreements_get_by_id", {"agreement_id": "CETA"})
    with InternaciaClient(db_path=v4_db) as client:
        assert call_tool(client, "intblock_lookup", {"id": "CETA"}) == {
            "id": "CETA",
            "name": "CETA",
        }
