"""Membership edges between international blocks and countries."""

from typing import cast

from internacia.database import DatabaseManager
from internacia.models import Membership
from internacia.views import relation


class MembershipsClient:
    """
    Client for the ``memberships`` edge table.

    ``current_only=True`` uses the ``current_memberships`` semantics from the internacia-db
    data contract: not ``former_member``, no ``left`` date, and the block is neither
    historical nor dissolved. Every participation status (member, observer, partner, …)
    is kept; filter ``status`` for full members.
    """

    def __init__(self, db_manager: DatabaseManager):
        self._db = db_manager

    def _source(self, current_only: bool) -> str:
        return relation(self._db, "current_memberships") if current_only else "memberships"

    def get_by_intblock(self, block_id: str, current_only: bool = True) -> list[Membership]:
        """
        Membership edges of one block, ordered by country code.

        Example:
            >>> nato = client.memberships.get_by_intblock("NATO")
            >>> [m["country_code"] for m in nato if m["status"] in ("member", "founding_member")]
        """
        query = (
            f"SELECT * FROM {self._source(current_only)} WHERE intblock_id = ? "
            "ORDER BY country_code"
        )
        return cast(list[Membership], self._db.execute_query_dict(query, (block_id.upper(),)))

    def get_by_country(self, country_code: str, current_only: bool = True) -> list[Membership]:
        """Membership edges of one country, ordered by block id."""
        query = (
            f"SELECT * FROM {self._source(current_only)} WHERE country_code = ? "
            "ORDER BY intblock_id"
        )
        return cast(list[Membership], self._db.execute_query_dict(query, (country_code.upper(),)))

    def is_member(self, country_code: str, block_id: str, current_only: bool = True) -> bool:
        """Whether the country has a membership edge (any status) in the block."""
        query = (
            f"SELECT 1 FROM {self._source(current_only)} "
            "WHERE country_code = ? AND intblock_id = ? LIMIT 1"
        )
        return bool(self._db.execute_query(query, (country_code.upper(), block_id.upper())))
