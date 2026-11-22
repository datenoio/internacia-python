"""Trade agreements registry (internacia-db 5.0 and later)."""

from typing import cast

from internacia.database import DatabaseManager
from internacia.models import CountryTradeAgreement, TradeAgreement, TradeAgreementParty


class TradeAgreementsClient:
    """
    Client for the ``trade_agreements`` and ``trade_agreement_parties`` tables and the
    ``country_trade_agreements`` view.

    internacia-db 5.0 added the registry and moved the two-party FTAs that used to be
    intblocks (``USKR``, ``CETA``, ``EUJP``, …) into it under the same id;
    ``client.intblocks.resolve_id`` reports them with ``target_dataset`` ``trade_agreements``.
    Some agreements with three or more parties (USMCA, CAFTADR, EEA) are also an intblock with
    the same id (``intblock_id``), which holds their roster. Databases before 5.0 have no
    registry: every method returns None or an empty list there.
    """

    def __init__(self, db_manager: DatabaseManager):
        self._db = db_manager

    def get_by_id(self, agreement_id: str) -> TradeAgreement | None:
        """
        One trade agreement, or None.

        Args:
            agreement_id: Agreement id (e.g. "USKR", "CETA", "USMCA")

        Example:
            >>> client.trade_agreements.get_by_id("CETA")["in_force"]  # "2017-09-21"
        """
        if not self._db.has_relation("trade_agreements"):
            return None
        rows = self._db.execute_query_dict(
            "SELECT * FROM trade_agreements WHERE id = ?", (agreement_id.upper(),)
        )
        return cast(TradeAgreement, rows[0]) if rows else None

    def get_parties(
        self, agreement_id: str, current_only: bool = False
    ) -> list[TradeAgreementParty]:
        """
        Parties of one trade agreement, ordered by party id.

        A bloc party (the EU) is one row with ``party_type`` ``intblock``; its members are
        in ``client.memberships``.

        Args:
            agreement_id: Agreement id (e.g. "USKR", "CETA", "USMCA")
            current_only: Leave out former parties (``former_party`` or a ``left`` date)
        """
        if not self._db.has_relation("trade_agreement_parties"):
            return []
        current = (
            " AND status IS DISTINCT FROM 'former_party' AND \"left\" IS NULL"
            if current_only
            else ""
        )
        query = (
            f"SELECT * FROM trade_agreement_parties WHERE agreement_id = ?{current} "
            "ORDER BY party_id"
        )
        return cast(
            list[TradeAgreementParty],
            self._db.execute_query_dict(query, (agreement_id.upper(),)),
        )

    def get_by_country(self, country_code: str) -> list[CountryTradeAgreement]:
        """
        Trade agreements a country is a current party to, ordered by agreement id.

        Includes agreements of a bloc it currently belongs to (``via`` is the bloc id, e.g.
        "EU"). ``agreement_status`` tells in-force agreements from signed, terminated or
        proposed ones.

        Args:
            country_code: Two-letter country code (e.g. "FR", "US")
        """
        if not self._db.has_relation("country_trade_agreements"):
            return []
        query = (
            "SELECT * FROM country_trade_agreements WHERE country_code = ? ORDER BY agreement_id"
        )
        return cast(
            list[CountryTradeAgreement],
            self._db.execute_query_dict(query, (country_code.upper(),)),
        )
