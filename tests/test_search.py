"""Search on a small real DuckDB: matching, ranking, deduplication, limits, escaping."""

import duckdb
import pytest

from internacia.database import DatabaseManager
from internacia.exceptions import ValidationError
from internacia.search import SearchClient


@pytest.fixture
def search(tmp_path):
    path = tmp_path / "search.duckdb"
    con = duckdb.connect(str(path))
    con.execute("""
        CREATE TABLE countries AS SELECT * FROM (VALUES
          ('US', 'USA', '840', 'United States', 'United States of America',
           MAP {'eng': {'official': 'United States of America', 'common': 'United States'}}),
          ('DE', 'DEU', '276', 'Germany', 'Federal Republic of Germany',
           MAP {'deu': {'official': 'Bundesrepublik Deutschland', 'common': 'Deutschland'}}),
          ('DK', 'DNK', '208', 'Denmark', 'Kingdom of Denmark', NULL),
          ('GB', 'GBR', '826', 'United Kingdom', 'United Kingdom of Great Britain', NULL)
        ) AS t(code, iso3code, numeric_code, name, official_name, native_names)
        """)
    con.execute("""
        CREATE TABLE intblocks AS SELECT * FROM (VALUES
          ('EU', 'European Union', [{'id': 'zh', 'name': '欧盟'}],
           [{'lang': 'en', 'value': 'EU'}], ['union']),
          ('UN', 'United Nations', NULL, [{'lang': 'fr', 'value': 'ONU'}], ['global']),
          ('USMCA', 'United States-Mexico-Canada Agreement', NULL, NULL, ['trade']),
          ('P5', '50% Club', NULL, NULL, NULL)
        ) AS t(id, name, other_names, acronyms, tags)
        """)
    con.close()
    return SearchClient(DatabaseManager(path))


def ids(results):
    return [r.get("code") or r.get("id") for r in results]


def test_exact_codes_rank_first(search):
    assert ids(search.fuzzy("US"))[0] == "US"
    assert ids(search.fuzzy("usa"))[0] == "US"
    assert ids(search.fuzzy("840")) == ["US"]
    assert ids(search.fuzzy("eu"))[0] == "EU"


def test_prefix_beats_contains_and_shorter_names_win(search):
    assert ids(search.fuzzy("united")) == ["US", "GB", "UN", "USMCA"]


def test_names_in_other_languages_and_acronyms(search):
    assert ids(search.fuzzy("Deutschland")) == ["DE"]
    assert ids(search.fuzzy("欧盟")) == ["EU"]
    assert ids(search.fuzzy("ONU")) == ["UN"]
    assert ids(search.fuzzy("trade")) == ["USMCA"]


def test_each_record_once_and_types(search):
    results = search.fuzzy("United States")
    assert ids(results) == ["US", "USMCA"]
    assert [r["type"] for r in results] == ["country", "intblock"]
    assert all("_rank" not in r and "_name_length" not in r for r in results)


def test_limit_and_scope(search):
    assert len(search.fuzzy("united", limit=2)) == 2
    assert ids(search.search_countries("united")) == ["US", "GB"]
    assert ids(search.search_intblocks("united")) == ["UN", "USMCA"]
    assert search.fuzzy("united", search_countries=False, search_intblocks=False) == []


def test_like_wildcards_match_literally(search):
    assert ids(search.fuzzy("50%")) == ["P5"]
    assert ids(search.fuzzy("%")) == ["P5"]
    assert search.fuzzy("_") == []


def test_results_are_plain_python(search):
    for row in search.fuzzy("Germany"):
        assert isinstance(row["native_names"], dict)


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"query": ""}, "query"),
        ({"query": "x", "limit": 0}, "limit"),
        ({"query": "x", "search_countries": "yes"}, "boolean"),
    ],
)
def test_validation(search, kwargs, message):
    with pytest.raises(ValidationError, match=message):
        search.fuzzy(**kwargs)
