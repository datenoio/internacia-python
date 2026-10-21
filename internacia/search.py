"""Search functionality with fuzzy matching support."""

import logging
from typing import Any, Dict, List, Set, Tuple, cast

from internacia.database import DatabaseManager
from internacia.exceptions import ValidationError
from internacia.models import SearchResult

logger = logging.getLogger(__name__)


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
        search_intblocks: bool = True
    ) -> List[SearchResult]:
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

        logger.debug("Fuzzy search: query='%s', limit=%s, countries=%s, blocks=%s",
                     query, limit, search_countries, search_intblocks)
        query_upper = query.upper()
        query_lower = query.lower()
        pattern = f"%{query_upper}%"
        results: List[Dict[str, Any]] = []

        if search_countries:
            results.extend(self._db.execute_query_dict(
                "SELECT *, 'country' as type FROM countries WHERE code = ? LIMIT ?",
                (query_upper, limit)
            ))
            results.extend(self._db.execute_query_dict(
                "SELECT *, 'country' as type FROM countries WHERE iso3code = ? LIMIT ?",
                (query_upper, limit)
            ))
            if query.isdigit():
                results.extend(self._db.execute_query_dict(
                    "SELECT *, 'country' as type FROM countries WHERE numeric_code = ? LIMIT ?",
                    (query, limit)
                ))
            results.extend(self._db.execute_query_dict(
                "SELECT *, 'country' as type FROM countries WHERE UPPER(name) LIKE ? LIMIT ?",
                (pattern, limit)
            ))
            results.extend(self._db.execute_query_dict(
                ("SELECT *, 'country' as type FROM countries "
                 "WHERE UPPER(official_name) LIKE ? LIMIT ?"),
                (pattern, limit)
            ))
            results.extend(self._db.execute_query_dict(
                """
                SELECT c.*, 'country' as type
                FROM countries c
                WHERE EXISTS (
                    SELECT 1 FROM UNNEST(map_values(c.native_names)) AS t(native)
                    WHERE UPPER(native.common) LIKE ? OR UPPER(native.official) LIKE ?
                )
                LIMIT ?
                """,
                (pattern, pattern, limit)
            ))

        if search_intblocks:
            results.extend(self._db.execute_query_dict(
                "SELECT *, 'intblock' as type FROM intblocks WHERE id = ? LIMIT ?",
                (query_upper, limit)
            ))
            results.extend(self._db.execute_query_dict(
                "SELECT *, 'intblock' as type FROM intblocks WHERE UPPER(name) LIKE ? LIMIT ?",
                (pattern, limit)
            ))
            results.extend(self._db.execute_query_dict(
                """
                SELECT i.*, 'intblock' as type
                FROM intblocks i
                WHERE EXISTS (
                    SELECT 1 FROM UNNEST(i.other_names) AS t(other)
                    WHERE UPPER(other.name) LIKE ?
                )
                LIMIT ?
                """,
                (pattern, limit)
            ))
            results.extend(self._db.execute_query_dict(
                """
                SELECT i.*, 'intblock' as type
                FROM intblocks i
                WHERE EXISTS (
                    SELECT 1 FROM UNNEST(i.acronyms) AS t(acr)
                    WHERE UPPER(acr.value) LIKE ?
                )
                LIMIT ?
                """,
                (pattern, limit)
            ))
            results.extend(self._db.execute_query_dict(
                """
                SELECT *, 'intblock' as type
                FROM intblocks
                WHERE LIST_CONTAINS(tags, ?)
                LIMIT ?
                """,
                (query_lower, limit)
            ))

        seen: Set[Tuple[str, Any]] = set()
        unique_results: List[Dict[str, Any]] = []
        for item in results:
            if item.get('type') == 'country':
                key = ('country', item.get('code'))
            else:
                key = ('intblock', item.get('id'))
            if key not in seen:
                seen.add(key)
                unique_results.append(item)

        def sort_key(item: Dict[str, Any]) -> Tuple[int, int]:
            name = str(item.get('name') or '').lower()
            code_or_id = str(item.get('code') or item.get('id') or '').lower()

            if code_or_id == query_lower:
                return (0, 0)
            if name.startswith(query_lower) or code_or_id.startswith(query_lower):
                return (1, len(name))
            return (2, len(name))

        unique_results.sort(key=sort_key)

        final_results = cast(List[SearchResult], unique_results[:limit])
        logger.debug("Fuzzy search returned %s results", len(final_results))
        return final_results

    def search_countries(
        self,
        query: str,
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Search only countries.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of matching country dictionaries
        """
        results = self.fuzzy(query, limit=limit, search_countries=True, search_intblocks=False)
        return [r for r in results if r.get('type') == 'country']

    def search_intblocks(
        self,
        query: str,
        limit: int = 10
    ) -> List[SearchResult]:
        """
        Search only international blocks.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of matching block dictionaries
        """
        results = self.fuzzy(query, limit=limit, search_countries=False, search_intblocks=True)
        return [r for r in results if r.get('type') == 'intblock']
