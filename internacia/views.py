"""Canonical internacia-db views, with their SQL as a fallback for older databases.

internacia-db ships these views inside ``internacia.duckdb`` from the release that added the
consumer contract; their definitions are part of ``contract.json``. internacia-db 3.0.0 has
no views, so the SDK runs the same SQL as a subquery there.
"""

from internacia.database import DatabaseManager

VIEW_SQL = {
    "current_memberships": (
        "SELECT m.* FROM memberships m JOIN intblocks i ON i.id = m.intblock_id "
        "WHERE m.status IS DISTINCT FROM 'former_member' AND m.\"left\" IS NULL "
        "AND i.status IS DISTINCT FROM 'historical' AND i.dissolved IS NULL"
    ),
    "country_currencies": (
        "SELECT c.code AS country_code, u.cur.code AS currency_code, "
        "u.cur.name AS currency_name, u.cur.symbol AS currency_symbol "
        "FROM countries c, UNNEST(c.currencies) AS u(cur)"
    ),
    "country_languages": (
        "SELECT c.code AS country_code, u.lang.code AS language_code, "
        "u.lang.name AS language_name, u.lang.official AS official "
        "FROM countries c, UNNEST(c.languages) AS u(lang)"
    ),
    "country_timezones": (
        "SELECT c.code AS country_code, u.tz AS timezone "
        "FROM countries c, UNNEST(c.timezones) AS u(tz)"
    ),
}


def relation(db: DatabaseManager, name: str) -> str:
    """SQL ``FROM`` target for a canonical view: the view itself, or its definition."""
    if db.has_relation(name):
        return name
    return f"({VIEW_SQL[name]}) AS {name}"
