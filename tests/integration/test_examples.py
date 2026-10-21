"""Run every script in examples/ against the real database."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

EXAMPLES_DIR = Path(__file__).resolve().parents[2] / "examples"
EXAMPLES = sorted(EXAMPLES_DIR.glob("*.py"))


def test_examples_found() -> None:
    assert EXAMPLES, f"no examples in {EXAMPLES_DIR}"


@pytest.mark.parametrize("script", EXAMPLES, ids=lambda p: p.name)
def test_example_runs(script: Path, real_db_path: Path) -> None:
    env = {**os.environ, "INTERNACIA_DB_PATH": str(real_db_path), "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.run(
        [sys.executable, str(script)],
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=300,
        check=False,
    )
    assert proc.returncode == 0, f"{script.name} failed:\n{proc.stdout[-2000:]}\n{proc.stderr}"
