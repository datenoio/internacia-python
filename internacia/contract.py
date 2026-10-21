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

# Contract major this SDK release supports.
SUPPORTED_CONTRACT_MAJOR = 3
# Newest contract this SDK release was tested against.
TESTED_CONTRACT = (3, 0)


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
    if major != SUPPORTED_CONTRACT_MAJOR:
        raise ContractError(
            f"internacia-db contract {major}.{minor} (data version {meta.get('version')}) is not "
            f"supported by this SDK, which requires contract {SUPPORTED_CONTRACT_MAJOR}.x. "
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
