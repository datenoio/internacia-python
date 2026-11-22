"""Data contract compatibility between this SDK and an internacia-db database.

internacia-db publishes ``contract_version`` (``MAJOR.MINOR``) in ``_meta`` and
``contract.json``. A different MAJOR means breaking changes, so the client refuses the
database; a newer MINOR only adds tables, columns or enum values, so it is accepted
with a warning.
"""

import logging
from typing import Any

from internacia.exceptions import ContractError

logger = logging.getLogger(__name__)

# Contract majors this SDK release supports, oldest first. internacia-db 4.0 changed what
# ``countries.native_names`` contains (only the country's own languages) and deprecated two
# membership statuses. internacia-db 5.0 added the trade agreements registry
# (``trade_agreements``, ``trade_agreement_parties``, ``country_trade_agreements``) and moved
# 34 two-party FTAs out of ``intblocks`` and ``memberships`` into it under the same id
# (``intblocks_aliases`` reason ``moved``, new column ``target_dataset``). In neither major did
# a table, column or type the SDK reads change, so the same code reads 3.x, 4.x and 5.x
# databases; ``client.trade_agreements`` returns nothing on databases before 5.0.
SUPPORTED_CONTRACT_MAJORS = (3, 4, 5)
# Newest supported contract major.
SUPPORTED_CONTRACT_MAJOR = SUPPORTED_CONTRACT_MAJORS[-1]
# Newest contract this SDK release was tested against.
TESTED_CONTRACT = (5, 0)


def supported_majors_text() -> str:
    """``"3.x, 4.x or 5.x"``: the supported contract majors, for messages."""
    names = [f"{major}.x" for major in SUPPORTED_CONTRACT_MAJORS]
    return " or ".join(filter(None, [", ".join(names[:-1]), names[-1]]))


def parse_contract(value: str) -> tuple[int, int]:
    """``"3.1"`` or a dataset version ``"3.1.2"`` → ``(3, 1)``."""
    parts = str(value).lstrip("v").split(".")
    try:
        return int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
    except ValueError as e:
        raise ContractError(f"Unrecognized contract version {value!r}") from e


def check_contract(meta: dict[str, Any]) -> None:
    """
    Raise ``ContractError`` if the database's contract major is not supported; log a
    warning if its minor is newer than the one this SDK was tested against.
    """
    major, minor = parse_contract(meta["contract_version"])
    if major not in SUPPORTED_CONTRACT_MAJORS:
        raise ContractError(
            f"internacia-db contract {major}.{minor} (data version {meta.get('version')}) is not "
            f"supported by this SDK, which requires contract {supported_majors_text()}. "
            "Use a matching internacia release or download a compatible database."
        )
    if (major, minor) > TESTED_CONTRACT:
        logger.warning(
            "internacia-db contract %s.%s is newer than %s.%s, which this SDK was tested against; "
            "new tables, columns or enum values may not be exposed",
            major,
            minor,
            *TESTED_CONTRACT,
        )
