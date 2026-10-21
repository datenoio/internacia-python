"""Countries data access module."""

import logging
from typing import cast

from internacia.database import DatabaseManager
from internacia.exceptions import ValidationError
from internacia.models import Country

logger = logging.getLogger(__name__)


class CountriesClient:
    """Client for querying countries data."""

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the countries client.

        Args:
            db_manager: Database manager instance
        """
        self._db = db_manager

    def get_by_code(self, code: str) -> Country | None:
        """
        Get a country by its ISO 3166-1 alpha-2 code.

        Args:
            code: Two-letter country code (e.g., "US", "FR", "GB")

        Returns:
            Country data as a dictionary, or None if not found

        Raises:
            ValidationError: If code is not a valid 2-letter string

        Example:
            >>> country = client.countries.get_by_code("US")
            >>> print(country["name"])  # "United States"
        """
        if not isinstance(code, str) or len(code) != 2 or not code.isalpha():
            raise ValidationError("code must be a 2-letter alphabetic string")

        logger.debug("Querying country by code: %s", code)
        query = "SELECT * FROM countries WHERE code = ?"
        results = cast(list[Country], self._db.execute_query_dict(query, (code.upper(),)))

        if results:
            logger.debug("Found country: %s", results[0].get("name"))
            return results[0]
        logger.debug("Country not found for code: %s", code)
        return None

    def get_by_iso3(self, iso3code: str) -> Country | None:
        """
        Get a country by its ISO 3166-1 alpha-3 code.

        Args:
            iso3code: Three-letter country code (e.g., "USA", "FRA", "GBR")

        Returns:
            Country data as a dictionary, or None if not found

        Raises:
            ValidationError: If iso3code is not a valid 3-letter string
        """
        if not isinstance(iso3code, str) or len(iso3code) != 3 or not iso3code.isalpha():
            raise ValidationError("iso3code must be a 3-letter alphabetic string")

        logger.debug("Querying country by ISO3 code: %s", iso3code)
        query = "SELECT * FROM countries WHERE iso3code = ?"
        results = cast(list[Country], self._db.execute_query_dict(query, (iso3code.upper(),)))

        if results:
            logger.debug("Found country: %s", results[0].get("name"))
            return results[0]
        logger.debug("Country not found for ISO3 code: %s", iso3code)
        return None

    def get_by_numeric_code(self, numeric_code: str) -> Country | None:
        """
        Get a country by its ISO 3166-1 numeric code.

        Args:
            numeric_code: Three-digit numeric code (e.g., "840", "250", "826")

        Returns:
            Country data as a dictionary, or None if not found

        Raises:
            ValidationError: If numeric_code is not a valid 3-digit string
        """
        if (
            not isinstance(numeric_code, str)
            or len(numeric_code) != 3
            or not numeric_code.isdigit()
        ):
            raise ValidationError("numeric_code must be a 3-digit string")

        logger.debug("Querying country by numeric code: %s", numeric_code)
        query = "SELECT * FROM countries WHERE numeric_code = ?"
        results = cast(list[Country], self._db.execute_query_dict(query, (numeric_code,)))

        if results:
            logger.debug("Found country: %s", results[0].get("name"))
            return results[0]
        logger.debug("Country not found for numeric code: %s", numeric_code)
        return None

    def get_all(self, limit: int | None = None) -> list[Country]:
        """
        Get all countries.

        Args:
            limit: Maximum number of results to return (optional)

        Returns:
            List of country dictionaries

        Raises:
            ValueError: If limit is not a positive integer
        """
        if limit is not None:
            if not isinstance(limit, int) or limit <= 0:
                raise ValueError("limit must be a positive integer")
            query = "SELECT * FROM countries LIMIT ?"
            return cast(list[Country], self._db.execute_query_dict(query, (limit,)))
        query = "SELECT * FROM countries"
        return cast(list[Country], self._db.execute_query_dict(query))

    def get_by_region(self, region_id: str) -> list[Country]:
        """
        Get countries by World Bank region ID.

        Args:
            region_id: Region ID (e.g., "NAC", "ECS", "SSF")

        Returns:
            List of country dictionaries
        """
        query = "SELECT * FROM countries WHERE region.id = ?"
        results = cast(list[Country], self._db.execute_query_dict(query, (region_id,)))
        return results

    def get_by_income_level(self, income_level_id: str) -> list[Country]:
        """
        Get countries by World Bank income level.

        Args:
            income_level_id: Income level ID (e.g., "OEC", "HIC", "LIC")

        Returns:
            List of country dictionaries
        """
        query = "SELECT * FROM countries WHERE incomeLevel.id = ?"
        results = cast(list[Country], self._db.execute_query_dict(query, (income_level_id,)))
        return results

    def get_un_members(self) -> list[Country]:
        """
        Get all UN member countries.

        Returns:
            List of UN member country dictionaries
        """
        query = "SELECT * FROM countries WHERE un_member = true"
        return cast(list[Country], self._db.execute_query_dict(query))

    def get_independent(self) -> list[Country]:
        """
        Get all independent countries.

        Returns:
            List of independent country dictionaries
        """
        query = "SELECT * FROM countries WHERE independent = true"
        return cast(list[Country], self._db.execute_query_dict(query))

    def get_by_continent(self, continent: str) -> list[Country]:
        """
        Get countries by continent.

        Args:
            continent: Continent name (e.g., "North America", "Europe", "Asia")

        Returns:
            List of country dictionaries
        """
        query = """
            SELECT * FROM countries
            WHERE LIST_CONTAINS(continents, ?)
        """
        results = cast(list[Country], self._db.execute_query_dict(query, (continent,)))
        return results

    def get_by_currency(self, currency_code: str) -> list[Country]:
        """
        Get countries that use a specific currency.

        Args:
            currency_code: Currency code (e.g., "USD", "EUR", "GBP")

        Returns:
            List of country dictionaries
        """
        query = """
            SELECT c.* FROM countries c
            WHERE EXISTS (
                SELECT 1 FROM UNNEST(c.currencies) AS t(curr) WHERE curr.code = ?
            )
        """
        results = cast(list[Country], self._db.execute_query_dict(query, (currency_code.upper(),)))
        return results

    def get_by_language(self, language_code: str) -> list[Country]:
        """
        Get countries where a specific language is spoken.

        Args:
            language_code: Language code (e.g., "eng", "fra", "spa")

        Returns:
            List of country dictionaries
        """
        query = """
            SELECT c.* FROM countries c
            WHERE EXISTS (
                SELECT 1 FROM UNNEST(c.languages) AS t(lang) WHERE lang.code = ?
            )
        """
        results = cast(list[Country], self._db.execute_query_dict(query, (language_code.lower(),)))
        return results

    def count(self) -> int:
        """
        Get the total number of countries.

        Returns:
            Total count of countries
        """
        query = "SELECT COUNT(*) as count FROM countries"
        result = self._db.execute_query_dict(query)
        return int(result[0]["count"]) if result else 0
