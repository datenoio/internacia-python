"""MCP server exposing the internacia SDK as tools (``pip install internacia[mcp]``).

Run ``internacia-mcp`` (stdio transport) and register it in an MCP client, for example::

    {"mcpServers": {"internacia": {"command": "internacia-mcp"}}}

The tools are the same as ``internacia.tools``: one per public SDK query method plus
``country_lookup`` and ``intblock_lookup``. The database is found the usual way
(``INTERNACIA_DB_PATH``, ``INTERNACIA_DATA_VERSION`` or the download cache).
"""

import inspect
import json
from typing import Any

from internacia import tools
from internacia.client import InternaciaClient
from internacia.version import __version__

INSTRUCTIONS = (
    "Reference data about countries and international organizations (internacia-db). "
    "Use country codes (ISO 3166-1 alpha-2) and intblock ids as join keys; memberships are "
    "current unless a tool's current_only argument is false."
)


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


def build_server(client: InternaciaClient | None = None) -> Any:
    """An ``MCPServer`` with every SDK tool registered against ``client``."""
    from mcp.server.mcpserver import MCPServer  # pylint: disable=import-outside-toplevel

    client = client or InternaciaClient()
    server = MCPServer(name="internacia", instructions=INSTRUCTIONS, version=__version__)
    for client_name, cls in tools.TOOL_CLIENTS.items():
        sub_client = getattr(client, client_name)
        for method_name, _ in inspect.getmembers(cls, inspect.isfunction):
            if not method_name.startswith("_"):
                server.add_tool(
                    getattr(sub_client, method_name),
                    name=f"{client_name}_{method_name}",
                    structured_output=False,
                )

    def country_lookup(
        code: str | None = None,
        iso3code: str | None = None,
        name: str | None = None,
        official_iso_only: bool = False,
    ) -> str:
        """Look up a country by alpha-2 code, alpha-3 code or name (retired codes remapped)."""
        args = {
            "code": code,
            "iso3code": iso3code,
            "name": name,
            "official_iso_only": official_iso_only,
        }
        return _json(tools.call_tool(client, "country_lookup", args))

    def intblock_lookup(
        id: str | None = None,  # noqa: A002  (matches the published tool schema)
        name: str | None = None,
        member_country: str | None = None,
        scope_category: str | None = None,
        blocktype: str | None = None,
    ) -> str:
        """Look up international organizations by id, name, current member country or block type."""
        args = {
            "id": id,
            "name": name,
            "member_country": member_country,
            "scope_category": scope_category,
            "blocktype": blocktype,
        }
        return _json(tools.call_tool(client, "intblock_lookup", args))

    server.add_tool(country_lookup, structured_output=False)
    server.add_tool(intblock_lookup, structured_output=False)
    return server


def main() -> None:
    """Entry point of ``internacia-mcp``: serve over stdio."""
    build_server().run("stdio")


if __name__ == "__main__":
    main()
