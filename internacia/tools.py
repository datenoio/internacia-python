"""LLM tool (function-calling) schemas generated from the SDK, and a dispatcher.

Every public query method of the SDK becomes one tool named ``<client>_<method>`` (for
example ``countries_get_by_code``). Names, descriptions and parameters are read from the
method signatures and docstrings, so the schemas cannot drift from the code. Two composite
tools, ``country_lookup`` and ``intblock_lookup``, keep the names of the schemas internacia-db
used to publish.

Pass a client to fill ``enum`` lists (regions, statuses, block types, …) from the connected
database. Enum-like fields are open in the internacia-db contract, so these lists describe
the data version in use rather than a fixed vocabulary.

Example:
    >>> from internacia import InternaciaClient
    >>> from internacia.tools import call_tool, openai_tools
    >>> client = InternaciaClient()
    >>> tools = openai_tools(client)  # pass to the OpenAI or any JSON-schema tool API
    >>> call_tool(client, "intblocks_get_by_id", {"block_id": "NATO"})["name"]
"""

import copy
import inspect
import json
import re
import types
import typing
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from internacia.blocktypes import BlocktypesClient
from internacia.client import InternaciaClient
from internacia.countries import CountriesClient
from internacia.intblocks import IntblocksClient
from internacia.memberships import MembershipsClient
from internacia.search import SearchClient

# InternaciaClient attribute -> class whose public methods become tools.
TOOL_CLIENTS: dict[str, type] = {
    "countries": CountriesClient,
    "intblocks": IntblocksClient,
    "memberships": MembershipsClient,
    "blocktypes": BlocktypesClient,
    "search": SearchClient,
}

# (tool name, parameter) -> SQL returning the values the connected database uses.
ENUM_QUERIES: dict[tuple[str, str], str] = {
    ("countries_get_by_region", "region_id"): "SELECT DISTINCT region.id FROM countries",
    ("countries_get_by_income_level", "income_level_id"): (
        "SELECT DISTINCT incomeLevel.id FROM countries"
    ),
    ("countries_get_by_continent", "continent"): (
        "SELECT DISTINCT u.x FROM countries, UNNEST(continents) AS u(x)"
    ),
    ("intblocks_get_by_status", "status"): "SELECT DISTINCT status FROM intblocks",
    ("intblocks_get_by_geographic_scope", "scope"): (
        "SELECT DISTINCT geographic_scope FROM intblocks"
    ),
    ("intblocks_get_by_blocktype", "blocktype"): "SELECT id FROM blocktypes",
    ("intblocks_get_by_topic", "topic_key"): (
        "SELECT DISTINCT u.t.key FROM intblocks, UNNEST(topics) AS u(t)"
    ),
    ("intblock_lookup", "scope_category"): "SELECT DISTINCT scope_category FROM intblocks",
    ("intblock_lookup", "blocktype"): "SELECT id FROM blocktypes",
}


@dataclass(frozen=True)
class Tool:
    """One tool: its JSON schema and the function that executes it."""

    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[..., Any]

    def schema(self) -> dict[str, Any]:
        return {"name": self.name, "description": self.description, "parameters": self.parameters}


_JSON_TYPES = {str: "string", int: "integer", float: "number", bool: "boolean"}


def _json_type(annotation: Any) -> str:
    if isinstance(annotation, types.UnionType) or typing.get_origin(annotation) is typing.Union:
        options = [a for a in typing.get_args(annotation) if a is not type(None)]
        return _json_type(options[0]) if len(options) == 1 else "string"
    return _JSON_TYPES.get(annotation, "string")


def _docstring_parts(func: Callable) -> tuple[str, dict[str, str]]:
    """Summary paragraph and ``Args:`` descriptions of a Google-style docstring."""
    doc = inspect.getdoc(func) or ""
    summary = doc.split("\n\n", 1)[0].replace("\n", " ").strip()
    args: dict[str, str] = {}
    match = re.search(r"^Args:\n(.*?)(?=^\S|\Z)", doc, re.M | re.S)
    if match:
        current = None
        for line in match.group(1).splitlines():
            item = re.match(r"\s{4}(\w+)(?:\s*\([^)]*\))?:\s*(.*)", line)
            if item:
                current = item.group(1)
                args[current] = item.group(2).strip()
            elif current and line.strip():
                args[current] += " " + line.strip()
    return summary, args


def _method_tool(client_name: str, method_name: str, method: Callable) -> Tool:
    summary, arg_docs = _docstring_parts(method)
    hints = typing.get_type_hints(method)
    properties: dict[str, Any] = {}
    required = []
    for name, param in inspect.signature(method).parameters.items():
        if name == "self":
            continue
        prop: dict[str, Any] = {"type": _json_type(hints.get(name, str))}
        if name in arg_docs:
            prop["description"] = arg_docs[name]
        if param.default is inspect.Parameter.empty:
            required.append(name)
        elif param.default is not None:
            prop["default"] = param.default
        properties[name] = prop
    parameters: dict[str, Any] = {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }

    def handler(client: InternaciaClient, **kwargs: Any) -> Any:
        return getattr(getattr(client, client_name), method_name)(**kwargs)

    return Tool(f"{client_name}_{method_name}", summary, parameters, handler)


def _country_lookup(client: InternaciaClient, **kwargs: Any) -> Any:
    countries = client.countries
    if kwargs.get("code"):
        resolved = countries.resolve_code(kwargs["code"])
        return countries.get_by_code(resolved["id"]) if resolved["id"] else None
    if kwargs.get("iso3code"):
        return countries.get_by_iso3(kwargs["iso3code"])
    if kwargs.get("name"):
        results = client.search.search_countries(kwargs["name"], limit=10)
        if kwargs.get("official_iso_only"):
            results = [r for r in results if r.get("code_status") == "official_iso3166_1"]
        return results
    raise ValueError("country_lookup needs one of: code, iso3code, name")


def _intblock_lookup(client: InternaciaClient, **kwargs: Any) -> Any:
    intblocks = client.intblocks
    if kwargs.get("id"):
        resolved = intblocks.resolve_id(kwargs["id"])
        return intblocks.get_by_id(resolved["id"]) if resolved["id"] else None
    results: list[Any]
    if kwargs.get("member_country"):
        results = intblocks.get_by_member(kwargs["member_country"], current_only=True)
    elif kwargs.get("name"):
        results = client.search.search_intblocks(kwargs["name"], limit=20)
    elif kwargs.get("blocktype"):
        results = intblocks.get_by_blocktype(kwargs["blocktype"])
    else:
        raise ValueError("intblock_lookup needs one of: id, member_country, name, blocktype")
    rows: list[dict[str, Any]] = [dict(r) for r in results]
    if kwargs.get("scope_category"):
        rows = [r for r in rows if r.get("scope_category") == kwargs["scope_category"]]
    if kwargs.get("blocktype"):
        rows = [r for r in rows if kwargs["blocktype"] in (r.get("blocktype") or [])]
    return rows


COMPOSITE_TOOLS = [
    Tool(
        "country_lookup",
        "Look up a country or territory by ISO 3166-1 alpha-2 code, alpha-3 code or name. "
        "Retired codes are remapped (KV -> XK).",
        {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "ISO 3166-1 alpha-2 code, e.g. FR."},
                "iso3code": {"type": "string", "description": "ISO 3166-1 alpha-3 code, e.g. FRA."},
                "name": {"type": "string", "description": "Country name in any language."},
                "official_iso_only": {
                    "type": "boolean",
                    "description": "With name: only current official ISO 3166-1 countries.",
                },
            },
            "required": [],
            "additionalProperties": False,
        },
        _country_lookup,
    ),
    Tool(
        "intblock_lookup",
        "Look up international organizations and groups (intblocks) by id, name, member "
        "country or block type. Retired ids are remapped through aliases; member_country "
        "returns current memberships only.",
        {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Intblock id, e.g. NATO, EU."},
                "name": {"type": "string", "description": "Organization name in any language."},
                "member_country": {
                    "type": "string",
                    "description": "Alpha-2 code of a current member, e.g. FR.",
                },
                "scope_category": {"type": "string", "description": "Optional filter."},
                "blocktype": {"type": "string", "description": "Block type, e.g. economic."},
            },
            "required": [],
            "additionalProperties": False,
        },
        _intblock_lookup,
    ),
]


def _all_tools() -> list[Tool]:
    tools = list(COMPOSITE_TOOLS)
    for client_name, cls in TOOL_CLIENTS.items():
        for method_name, method in inspect.getmembers(cls, inspect.isfunction):
            if not method_name.startswith("_"):
                tools.append(_method_tool(client_name, method_name, method))
    return tools


def _with_enums(tool: Tool, client: InternaciaClient | None) -> dict[str, Any]:
    schema = copy.deepcopy(tool.schema())
    if client is None:
        return schema
    for (name, param), query in ENUM_QUERIES.items():
        if name == tool.name and param in schema["parameters"]["properties"]:
            rows = client._db_manager.execute_query(query)  # pylint: disable=protected-access
            values = sorted({str(row[0]) for row in rows if row[0] is not None})
            if values:
                schema["parameters"]["properties"][param]["enum"] = values
    return schema


def tool_schemas(client: InternaciaClient | None = None) -> list[dict[str, Any]]:
    """Tool definitions as ``{"name", "description", "parameters"}`` (JSON Schema)."""
    return [_with_enums(tool, client) for tool in _all_tools()]


def openai_tools(client: InternaciaClient | None = None) -> list[dict[str, Any]]:
    """Tool definitions in the OpenAI Chat Completions ``tools`` format."""
    return [{"type": "function", "function": schema} for schema in tool_schemas(client)]


def call_tool(client: InternaciaClient, name: str, arguments: dict[str, Any] | str) -> Any:
    """
    Execute a tool call and return a JSON-serializable result.

    Args:
        client: Client to run the query with
        name: Tool name from ``tool_schemas()``
        arguments: Tool arguments as a dict or a JSON string (as LLM APIs return them)

    Raises:
        KeyError: If the tool does not exist
    """
    args = json.loads(arguments) if isinstance(arguments, str) else dict(arguments)
    tool = next((t for t in _all_tools() if t.name == name), None)
    if tool is None:
        raise KeyError(f"Unknown tool: {name}")
    return tool.handler(client, **args)
