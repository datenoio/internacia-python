"""Block type taxonomy."""

from typing import cast

from internacia.database import DatabaseManager
from internacia.models import Blocktype


class BlocktypesClient:
    """Client for the ``blocktypes`` table (the values allowed in ``intblocks.blocktype``)."""

    def __init__(self, db_manager: DatabaseManager):
        self._db = db_manager

    def get_all(self) -> list[Blocktype]:
        """All block types, ordered by id."""
        return cast(
            list[Blocktype], self._db.execute_query_dict("SELECT * FROM blocktypes ORDER BY id")
        )

    def get_by_id(self, blocktype_id: str) -> Blocktype | None:
        """One block type, or None."""
        rows = self._db.execute_query_dict(
            "SELECT * FROM blocktypes WHERE id = ?", (blocktype_id.lower(),)
        )
        return cast(Blocktype, rows[0]) if rows else None
