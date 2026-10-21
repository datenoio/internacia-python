"""Resolution of retired, renamed and merged identifiers through internacia-db alias tables."""

from internacia.database import DatabaseManager
from internacia.models import IdResolution


def resolve(
    db: DatabaseManager, table: str, key: str, alias_table: str, value: str
) -> IdResolution:
    """
    Resolve ``value`` against ``table.key`` and the alias table.

    Databases without alias tables (internacia-db 3.0.0) can only report ``current`` or
    ``unknown``.
    """
    exists = bool(db.execute_query(f"SELECT 1 FROM {table} WHERE {key} = ? LIMIT 1", (value,)))
    alias = None
    if db.has_relation(alias_table):
        rows = db.execute_query_dict(f"SELECT * FROM {alias_table} WHERE alias = ?", (value,))
        alias = rows[0] if rows else None
    result: IdResolution = {
        "input": value,
        "id": value if exists else None,
        "status": "current" if exists else "unknown",
        "since": None,
        "note": None,
        "disambiguated": None,
    }
    if alias is None:
        return result
    result["since"] = alias.get("since") or None
    result["note"] = alias.get("note") or None
    if exists:
        if alias.get("reason") == "disambiguated":
            result["disambiguated"] = alias.get("target") or None
        return result
    result["status"] = alias.get("reason") or "renamed"
    result["id"] = alias.get("target") or None
    return result
