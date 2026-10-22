"""Countries data access module."""

import logging
from typing import cast

from internacia.aliases import resolve
from internacia.database import DatabaseManager
from internacia.exceptions import ValidationError
from internacia.models import (
    Country,
    Currency,
    CurrencyEntry,
    IdResolution,
    Language,
    LanguageEntry,
    RegionEntry,
    TimezoneEntry,
)
from internacia.views import relation

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

    def resolve_code(self, code: str) -> IdResolution:
        """
        Resolve a stored country code that may have been renamed (e.g. ``KV`` → ``XK``).

        See ``IntblocksClient.resolve_id`` for the result fields.
        """
        return resolve(self._db, "countries", "code", "countries_aliases", code.upper())

    def get_currencies(self) -> list[CurrencyEntry]:
        """All currencies used by countries, with ``country_count``, ordered by code."""
        query = f"""
            SELECT currency_code AS code, min(currency_name) AS name,
                   min(currency_symbol) AS symbol, count(*) AS country_count
            FROM {relation(self._db, "country_currencies")}
            GROUP BY currency_code ORDER BY currency_code
        """
        return cast(list[CurrencyEntry], self._db.execute_query_dict(query))

    def get_currency(self, currency_code: str) -> CurrencyEntry | None:
        """One currency by ISO 4217 code, or None."""
        code = currency_code.upper()
        return next((c for c in self.get_currencies() if c["code"] == code), None)

    def get_country_currencies(self, country_code: str) -> list[Currency]:
        """Currencies of one country (empty if it has none or does not exist)."""
        query = f"""
            SELECT currency_code AS code, currency_name AS name, currency_symbol AS symbol
            FROM {relation(self._db, "country_currencies")}
            WHERE country_code = ? ORDER BY currency_code
        """
        return cast(list[Currency], self._db.execute_query_dict(query, (country_code.upper(),)))

    def get_languages(self) -> list[LanguageEntry]:
        """All languages listed for countries, with ``country_count``, ordered by code."""
        query = f"""
            SELECT language_code AS code, min(language_name) AS name,
                   count(*) AS country_count
            FROM {relation(self._db, "country_languages")}
            GROUP BY language_code ORDER BY language_code
        """
        return cast(list[LanguageEntry], self._db.execute_query_dict(query))

    def get_language(self, language_code: str) -> LanguageEntry | None:
        """One language by ISO 639-3 code, or None."""
        code = language_code.lower()
        return next((lang for lang in self.get_languages() if lang["code"] == code), None)

    def get_country_languages(self, country_code: str) -> list[Language]:
        """Languages of one country (empty if it has none or does not exist)."""
        query = f"""
            SELECT language_code AS code, language_name AS name, official
            FROM {relation(self._db, "country_languages")}
            WHERE country_code = ? ORDER BY language_code
        """
        return cast(list[Language], self._db.execute_query_dict(query, (country_code.upper(),)))

    def get_timezones(self) -> list[TimezoneEntry]:
        """All IANA time zones used by countries, with ``country_count``."""
        query = f"""
            SELECT timezone, count(*) AS country_count
            FROM {relation(self._db, "country_timezones")}
            GROUP BY timezone ORDER BY timezone
        """
        return cast(list[TimezoneEntry], self._db.execute_query_dict(query))

    def get_country_timezones(self, country_code: str) -> list[str]:
        """Time zones of one country (empty if it has none or does not exist)."""
        query = f"""
            SELECT timezone FROM {relation(self._db, "country_timezones")}
            WHERE country_code = ? ORDER BY timezone
        """
        return [row[0] for row in self._db.execute_query(query, (country_code.upper(),))]

    def get_by_timezone(self, timezone: str) -> list[Country]:
        """Countries that use an IANA time zone (exact, case-sensitive name)."""
        query = f"""
            SELECT c.* FROM countries c
            WHERE c.code IN (
                SELECT country_code FROM {relation(self._db, "country_timezones")}
                WHERE timezone = ?
            )
            ORDER BY c.code
        """
        return cast(list[Country], self._db.execute_query_dict(query, (timezone,)))

    def get_regions(self) -> list[RegionEntry]:
        """World Bank regions with ``country_count``, ordered by id."""
        query = """
            SELECT region.id AS id, min(region.value) AS value, count(*) AS country_count
            FROM countries WHERE region.id IS NOT NULL
            GROUP BY region.id ORDER BY region.id
        """
        return cast(list[RegionEntry], self._db.execute_query_dict(query))

    def get_region(self, region_id: str) -> RegionEntry | None:
        """One World Bank region by id (e.g. ``ECS``), or None."""
        code = region_id.upper()
        return next((r for r in self.get_regions() if r["id"] == code), None)
