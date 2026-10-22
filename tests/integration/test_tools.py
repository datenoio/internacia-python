"""LLM tools against a real database: enum lists and dispatch."""

import json

import pytest

from internacia import InternaciaClient
from internacia.tools import call_tool, tool_schemas

SAMPLE_ARGS = {
    "code": "FR",
    "iso3code": "FRA",
    "numeric_code": "250",
    "region_id": "ECS",
    "income_level_id": "LMC",
    "continent": "Europe",
    "currency_code": "EUR",
    "language_code": "fra",
    "country_code": "FR",
    "timezone": "Europe/Paris",
    "block_id": "NATO",
    "blocktype": "economic",
    "blocktype_id": "economic",
    "status": "formal",
    "scope": "regional",
    "acronym": "NATO",
    "tag": "trade",
    "topic_key": "economy",
    "year": 1945,
    "query": "France",
    "limit": 3,
}


def test_enum_lists_come_from_the_data(client: InternaciaClient) -> None:
    schemas = {s["name"]: s for s in tool_schemas(client)}
    status = schemas["intblocks_get_by_status"]["parameters"]["properties"]["status"]
    assert {"formal", "historical"} <= set(status["enum"])
    region = schemas["countries_get_by_region"]["parameters"]["properties"]["region_id"]
    assert "ECS" in region["enum"]
    blocktype = schemas["intblock_lookup"]["parameters"]["properties"]["blocktype"]
    assert "economic" in blocktype["enum"]


@pytest.mark.parametrize("schema", tool_schemas(), ids=lambda s: s["name"])
def test_every_tool_runs_and_returns_json(client: InternaciaClient, schema: dict) -> None:
    props = schema["parameters"]["properties"]
    if schema["name"] == "country_lookup":
        args = {"code": "KV" if client.countries.resolve_code("KV")["id"] else "FR"}
    elif schema["name"] == "intblock_lookup":
        args = {"member_country": "FR", "scope_category": "igo"}
    else:
        args = {k: SAMPLE_ARGS[k] for k in schema["parameters"]["required"]}
        if "limit" in props:
            args["limit"] = SAMPLE_ARGS["limit"]
    result = call_tool(client, schema["name"], json.dumps(args))
    json.dumps(result, default=str)
    assert result not in (None, [], {}) or schema["name"].endswith("count")


def test_lookup_tools(client: InternaciaClient) -> None:
    assert call_tool(client, "country_lookup", {"name": "Deutschland"})[0]["code"] == "DE"
    assert call_tool(client, "intblock_lookup", {"id": "nato"})["id"] == "NATO"
    with pytest.raises(ValueError):
        call_tool(client, "intblock_lookup", {})
