"""scripts/data_bump.py: moving the tested internacia-db release forward."""

import importlib.util
import json
import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("data_bump", REPO / "scripts" / "data_bump.py")
data_bump = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(data_bump)  # type: ignore[union-attr]


@pytest.fixture
def root(tmp_path, monkeypatch):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "internacia-db.json").write_text(
        json.dumps({"version": "3.0.0", "sha256": "a" * 64}), encoding="utf-8"
    )
    (tmp_path / "internacia").mkdir()
    # The fixture pretends the SDK was last tested at contract 3.0, independent of the
    # live pin, so a later data bump does not make these cases assert the old file.
    contract = (REPO / "internacia" / "contract.py").read_text(encoding="utf-8")
    contract = re.sub(
        r"(?m)^TESTED_CONTRACT = \(\d+, \d+\)$",
        "TESTED_CONTRACT = (3, 0)",
        contract,
        count=1,
    )
    (tmp_path / "internacia" / "contract.py").write_text(contract, encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "| 0.4.x | 3.x (contract 3.x; tested against 3.0.0) |\n"
        "| 0.3.x | 3.x (tested against 3.0.0) |\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(data_bump, "ROOT", tmp_path)
    monkeypatch.setattr(data_bump, "TESTED_CONTRACT", (3, 0))
    monkeypatch.setattr(data_bump, "database_sha256", lambda tag: "b" * 64)
    monkeypatch.delenv("GITHUB_OUTPUT", raising=False)
    return tmp_path


def _outputs(path: Path) -> dict[str, str]:
    return dict(line.split("=", 1) for line in path.read_text().splitlines())


def test_minor_release_is_bumped_and_auto_merged(root, monkeypatch, tmp_path_factory):
    out = tmp_path_factory.mktemp("gh") / "output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(out))
    monkeypatch.setattr(data_bump, "_latest_release_tag", lambda: "v3.1.0")
    monkeypatch.setattr("sys.argv", ["data_bump.py", "--pr-body", str(root / "body.md")])

    assert data_bump.main() == 0

    assert json.loads((root / "tests" / "internacia-db.json").read_text()) == {
        "version": "3.1.0",
        "sha256": "b" * 64,
    }
    assert "TESTED_CONTRACT = (3, 1)" in (root / "internacia" / "contract.py").read_text()
    readme = (root / "README.md").read_text()
    assert "tested against 3.1.0) |\n| 0.3.x | 3.x (tested against 3.0.0)" in readme
    assert _outputs(out) == {
        "changed": "true",
        "version": "3.1.0",
        "previous": "3.0.0",
        "auto_merge": "true",
    }
    assert "merges automatically" in (root / "body.md").read_text()


def test_patch_release_keeps_tested_contract(root, monkeypatch):
    monkeypatch.setattr("sys.argv", ["data_bump.py", "--version", "3.0.1"])
    assert data_bump.main() == 0
    assert json.loads((root / "tests" / "internacia-db.json").read_text())["version"] == "3.0.1"
    assert "TESTED_CONTRACT = (3, 0)" in (root / "internacia" / "contract.py").read_text()


def test_new_major_is_not_auto_merged(root, monkeypatch, tmp_path_factory):
    out = tmp_path_factory.mktemp("gh") / "output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(out))
    monkeypatch.setattr(
        "sys.argv", ["data_bump.py", "--version", "v4.0.0", "--pr-body", str(root / "body.md")]
    )
    assert data_bump.main() == 0
    assert _outputs(out)["auto_merge"] == "false"
    assert "TESTED_CONTRACT = (3, 0)" in (root / "internacia" / "contract.py").read_text()
    assert "Contract major changed" in (root / "body.md").read_text()


def test_up_to_date(root, monkeypatch, tmp_path_factory):
    out = tmp_path_factory.mktemp("gh") / "output"
    monkeypatch.setenv("GITHUB_OUTPUT", str(out))
    monkeypatch.setattr(data_bump, "_latest_release_tag", lambda: "v3.0.0")
    monkeypatch.setattr("sys.argv", ["data_bump.py"])
    assert data_bump.main() == 0
    assert _outputs(out)["changed"] == "false"
    assert json.loads((root / "tests" / "internacia-db.json").read_text())["version"] == "3.0.0"


def test_pin_matches_the_test_database_in_use():
    pin = json.loads((REPO / "tests" / "internacia-db.json").read_text())
    assert data_bump.parse_version(pin["version"]) is not None
    assert len(pin["sha256"]) == 64
