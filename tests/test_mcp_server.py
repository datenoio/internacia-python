"""MCP server registration (``internacia[mcp]``); calls against data are in integration."""

import asyncio

import pytest

from internacia import InternaciaClient, tools

pytest.importorskip("mcp")

from internacia.mcp_server import build_server  # noqa: E402


def test_tools_match_the_llm_tool_schemas(mock_db_path):
    server = build_server(InternaciaClient(db_path=mock_db_path))
    listed = {tool.name: tool for tool in asyncio.run(server.list_tools())}
    assert set(listed) == {schema["name"] for schema in tools.tool_schemas()}
    assert all(tool.description for tool in listed.values())
    members = listed["memberships_get_by_intblock"].input_schema
    assert members["required"] == ["block_id"]
    assert set(listed["intblock_lookup"].input_schema["properties"]) == {
        "id",
        "name",
        "member_country",
        "scope_category",
        "blocktype",
    }
