"""Point the SDK's tests at the newest internacia-db release.

Used by .github/workflows/data-bump.yml (daily, and on the ``internacia-db-release`` dispatch
that internacia-db sends after a release). It updates:

- ``tests/internacia-db.json``: the release CI downloads for the integration tests;
- ``TESTED_CONTRACT`` in ``internacia/contract.py`` when the release has a newer contract minor;
- the "tested against" version in the README compatibility table.

A release with a different contract major is still written to ``tests/internacia-db.json`` so
the pull request shows what fails, but it is not marked for auto-merge.

Usage:
    python scripts/data_bump.py [--version 3.1.0] [--pr-body data-bump.md]
"""

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

import requests

from internacia.contract import SUPPORTED_CONTRACT_MAJOR, TESTED_CONTRACT, parse_contract
from internacia.downloader import (
    DB_FILE,
    DOWNLOAD_URL,
    _fetch_checksums,
    _latest_release_tag,
    parse_version,
    release_tag,
)

ROOT = Path(__file__).resolve().parents[1]


def database_sha256(tag: str) -> str:
    """The release's SHA-256 of internacia.duckdb: from SHA256SUMS, else by downloading it."""
    checksums = _fetch_checksums(tag)
    if checksums and DB_FILE in checksums:
        return checksums[DB_FILE]
    digest = hashlib.sha256()
    with (
        tempfile.TemporaryFile() as tmp,
        requests.get(
            DOWNLOAD_URL.format(tag=tag, name=DB_FILE), stream=True, timeout=120
        ) as response,
    ):
        response.raise_for_status()
        for chunk in response.iter_content(1 << 20):
            digest.update(chunk)
            tmp.write(chunk)
    return digest.hexdigest()


def bump(version: str, sha256: str, root: Path) -> list[str]:
    """Write ``version`` to the pin, TESTED_CONTRACT and the README; return what changed."""
    changed = []
    pin = root / "tests" / "internacia-db.json"
    pin.write_text(
        json.dumps({"version": version, "sha256": sha256}, indent=2) + "\n", encoding="utf-8"
    )
    changed.append("tests/internacia-db.json")

    contract = parse_contract(version)
    if contract[0] == SUPPORTED_CONTRACT_MAJOR and contract > TESTED_CONTRACT:
        path = root / "internacia" / "contract.py"
        text, count = re.subn(
            r"(?m)^TESTED_CONTRACT = \(\d+, \d+\)$",
            f"TESTED_CONTRACT = ({contract[0]}, {contract[1]})",
            path.read_text(encoding="utf-8"),
        )
        if count == 1:
            path.write_text(text, encoding="utf-8")
            changed.append("internacia/contract.py")

    readme = root / "README.md"
    text, count = re.subn(
        r"tested against \d+\.\d+\.\d+",
        f"tested against {version}",
        readme.read_text(encoding="utf-8"),
        count=1,
    )
    if count:
        readme.write_text(text, encoding="utf-8")
        changed.append("README.md")
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--version", help="internacia-db release (default: the latest)")
    parser.add_argument("--pr-body", type=Path, help="write the pull request body here")
    args = parser.parse_args()

    tag = release_tag(args.version) if args.version else _latest_release_tag()
    version = tag.removeprefix("v")
    current = json.loads((ROOT / "tests" / "internacia-db.json").read_text(encoding="utf-8"))[
        "version"
    ]
    outputs = {"changed": "false", "version": version, "previous": current, "auto_merge": "false"}

    new, old = parse_version(version), parse_version(current)
    if new is None or old is None:
        print(f"Unrecognized version: {version!r} or {current!r}", file=sys.stderr)
        return 1
    if new <= old:
        print(f"Already tested against internacia-db {current} (latest: {version})")
    else:
        same_major = parse_contract(version)[0] == SUPPORTED_CONTRACT_MAJOR
        changed = bump(version, database_sha256(tag), ROOT)
        outputs.update(changed="true", auto_merge=str(same_major).lower())
        print(f"internacia-db {current} -> {version}; updated {', '.join(changed)}")
        if args.pr_body:
            args.pr_body.write_text(
                pr_body(current, version, same_major, changed), encoding="utf-8"
            )

    if github_output := os.environ.get("GITHUB_OUTPUT"):
        with open(github_output, "a", encoding="utf-8") as f:
            f.writelines(f"{key}={value}\n" for key, value in outputs.items())
    return 0


def pr_body(current: str, version: str, same_major: bool, changed: list[str]) -> str:
    notes = (
        "Same contract major, so this merges automatically once CI passes. "
        "No SDK release is needed unless the release adds tables or columns the SDK should expose."
        if same_major
        else f"**Contract major changed** (SDK supports {SUPPORTED_CONTRACT_MAJOR}.x): "
        "CI is expected to fail until the SDK supports the new contract. Not set to auto-merge."
    )
    files = "\n".join(f"- `{path}`" for path in changed)
    return (
        f"Runs the SDK's integration and contract tests against internacia-db **{version}** "
        f"(was {current}).\n\n{notes}\n\nRelease notes: "
        f"https://github.com/datenoio/internacia-db/releases/tag/v{version}\n\nChanged:\n{files}\n"
    )


if __name__ == "__main__":
    sys.exit(main())
