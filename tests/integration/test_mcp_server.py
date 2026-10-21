"""MCP tool calls against a real database."""

import asyncio
import json

import pytest

from internacia import InternaciaClient

pytest.importorskip("mcp")

from internacia.mcp_server import build_server  # noqa: E402


def _call(client: InternaciaClient, name: str, args: dict) -> object:
    result = asyncio.run(build_server(client).call_tool(name, args))
    assert not result.is_error, result
    return json.loads(result.content[0].text)


def test_sdk_method_tool(client: InternaciaClient) -> None:
    block = _call(client, "intblocks_get_by_id", {"block_id": "NATO"})
    assert block["id"] == "NATO"


def test_composite_tool(client: InternaciaClient) -> None:
    country = _call(client, "country_lookup", {"code": "FR"})
    assert country["iso3code"] == "FRA"
    blocks = _call(client, "intblock_lookup", {"member_country": "FR", "blocktype": "military"})
    assert any(block["id"] == "NATO" for block in blocks)
