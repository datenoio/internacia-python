"""LLM tool schemas generated from the SDK (no database needed)."""

import inspect
import json

import pytest

from internacia import tools


@pytest.fixture(scope="module")
def schemas():
    return {schema["name"]: schema for schema in tools.tool_schemas()}


def test_every_public_method_is_a_tool(schemas):
    for client_name, cls in tools.TOOL_CLIENTS.items():
        for method_name, _ in inspect.getmembers(cls, inspect.isfunction):
            if not method_name.startswith("_"):
                assert f"{client_name}_{method_name}" in schemas
    assert {"country_lookup", "intblock_lookup"} <= set(schemas)


def test_schemas_are_valid_json_schema_objects(schemas):
    for name, schema in schemas.items():
        params = schema["parameters"]
        assert schema["description"], name
        assert params["type"] == "object" and params["additionalProperties"] is False
        assert set(params["required"]) <= set(params["properties"])
        for prop in params["properties"].values():
            assert prop["type"] in {"string", "integer", "number", "boolean"}
    json.dumps(schemas)


def test_signature_types_defaults_and_docs(schemas):
    members = schemas["memberships_get_by_intblock"]["parameters"]
    assert members["required"] == ["block_id"]
    assert members["properties"]["current_only"] == {"type": "boolean", "default": True}
    limit = schemas["countries_get_all"]["parameters"]["properties"]["limit"]
    assert limit["type"] == "integer" and "default" not in limit
    region = schemas["countries_get_by_region"]["parameters"]["properties"]["region_id"]
    assert "ECS" in region["description"]
    assert "enum" not in region  # enums only with a client


def test_openai_format():
    first = tools.openai_tools()[0]
    assert first["type"] == "function"
    assert set(first["function"]) == {"name", "description", "parameters"}


def test_unknown_tool(mock_db_path):
    from internacia import InternaciaClient

    with pytest.raises(KeyError):
        tools.call_tool(InternaciaClient(db_path=mock_db_path), "drop_tables", {})
