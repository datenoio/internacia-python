"""Search functionality with fuzzy matching support."""

import logging
from typing import Any, cast

from internacia.database import DatabaseManager
from internacia.exceptions import ValidationError
from internacia.models import SearchResult

logger = logging.getLogger(__name__)


def _escape_like(text: str) -> str:
    """Escape LIKE wildcards so they match literally (used with ``ESCAPE '\\'``)."""
    return text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


# One query per table. _rank: 0 exact code/id, 1 name or code/id starts with the query,
# 2 any other match; ties go to shorter names.
COUNTRY_SEARCH_SQL = r"""
SELECT * FROM (
    SELECT c.*, 'country' AS type,
        CASE
            WHEN c.code = $upper OR c.iso3code = $upper OR c.numeric_code = $raw THEN 0
            WHEN lower(c.name) LIKE $prefix ESCAPE '\'
              OR lower(c.code) LIKE $prefix ESCAPE '\' THEN 1
            ELSE 2
        END AS _rank,
        length(c.name) AS _name_length
    FROM countries c
    WHERE c.code = $upper
       OR c.iso3code = $upper
       OR c.numeric_code = $raw
       OR upper(c.name) LIKE $pattern ESCAPE '\'
       OR upper(c.official_name) LIKE $pattern ESCAPE '\'
       OR EXISTS (
            SELECT 1 FROM UNNEST(map_values(c.native_names)) AS t(native)
            WHERE upper(native.common) LIKE $pattern ESCAPE '\'
               OR upper(native.official) LIKE $pattern ESCAPE '\'
       )
)
ORDER BY _rank, _name_length, code
LIMIT $limit
"""

INTBLOCK_SEARCH_SQL = r"""
SELECT * FROM (
    SELECT i.*, 'intblock' AS type,
        CASE
            WHEN i.id = $upper THEN 0
            WHEN lower(i.name) LIKE $prefix ESCAPE '\'
              OR lower(i.id) LIKE $prefix ESCAPE '\' THEN 1
            ELSE 2
        END AS _rank,
        length(i.name) AS _name_length
    FROM intblocks i
    WHERE i.id = $upper
       OR upper(i.name) LIKE $pattern ESCAPE '\'
       OR EXISTS (
            SELECT 1 FROM UNNEST(i.other_names) AS t(other)
            WHERE upper(other.name) LIKE $pattern ESCAPE '\'
       )
       OR EXISTS (
            SELECT 1 FROM UNNEST(i.acronyms) AS t(acr)
            WHERE upper(acr.value) LIKE $pattern ESCAPE '\'
       )
       OR list_contains(i.tags, $lower)
)
ORDER BY _rank, _name_length, id
LIMIT $limit
"""


class SearchClient:
    """Client for searching countries and international blocks."""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the search client.

        Args:
            db_manager: Database manager instance
        """
        self._db = db_manager

    def fuzzy(
        self,
        query: str,
        limit: int = 10,
        search_countries: bool = True,
        search_intblocks: bool = True,
    ) -> list[SearchResult]:
        """
        Perform fuzzy search across countries and international blocks.

        This function searches across:
        - Country names (in any language via native_names)
        - Country codes (ISO 3166-1 alpha-2, alpha-3, numeric)
        - International block names
        - Block names in other languages (other_names)
        - Block acronyms (in any language)
        - Block IDs

        Args:
            query: Search query string
            limit: Maximum number of results to return
            search_countries: Whether to search countries (default: True)
            search_intblocks: Whether to search international blocks (default: True)

        Returns:
            List of matching records with a 'type' field indicating 'country' or 'intblock'

        Raises:
            ValidationError: If query is empty or limit is invalid
            DatabaseError: If a search query fails

        Example:
            >>> results = client.search.fuzzy("United States")
            >>> results = client.search.fuzzy("EU", search_countries=False)
            >>> results = client.search.fuzzy("Европа", limit=5)
        """
        if not isinstance(query, str) or not query.strip():
            raise ValidationError("query must be a non-empty string")
        if not isinstance(limit, int) or limit <= 0:
            raise ValidationError("limit must be a positive integer")
        if not isinstance(search_countries, bool) or not isinstance(search_intblocks, bool):
            raise ValidationError("search_countries and search_intblocks must be boolean")

        logger.debug(
            "Fuzzy search: query='%s', limit=%s, countries=%s, blocks=%s",
            query,
            limit,
            search_countries,
            search_intblocks,
        )
        needle = query.strip()
        upper = needle.upper()
        pattern = "%" + _escape_like(upper) + "%"
        prefix = _escape_like(needle.lower()) + "%"
        params = {
            "upper": upper,
            "raw": needle,
            "lower": needle.lower(),
            "pattern": pattern,
            "prefix": prefix,
            "limit": limit,
        }
        candidates: list[dict[str, Any]] = []
        if search_countries:
            country_params = {k: v for k, v in params.items() if k != "lower"}
            candidates += self._db.execute_query_dict(COUNTRY_SEARCH_SQL, country_params)
        if search_intblocks:
            block_params = {k: v for k, v in params.items() if k != "raw"}
            candidates += self._db.execute_query_dict(INTBLOCK_SEARCH_SQL, block_params)
        candidates.sort(key=lambda row: (row["_rank"], row["_name_length"]))
        results = []
        for row in candidates[:limit]:
            row.pop("_rank")
            row.pop("_name_length")
            results.append(row)
        logger.debug("Fuzzy search returned %s results", len(results))
        return cast(list[SearchResult], results)

    def search_countries(self, query: str, limit: int = 10) -> list[SearchResult]:
        """
        Search only countries.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of matching country dictionaries
        """
        results = self.fuzzy(query, limit=limit, search_countries=True, search_intblocks=False)
        return [r for r in results if r.get("type") == "country"]

    def search_intblocks(self, query: str, limit: int = 10) -> list[SearchResult]:
        """
        Search only international blocks.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of matching block dictionaries
        """
        results = self.fuzzy(query, limit=limit, search_countries=False, search_intblocks=True)
        return [r for r in results if r.get("type") == "intblock"]
