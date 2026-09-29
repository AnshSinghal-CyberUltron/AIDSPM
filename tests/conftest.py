from __future__ import annotations

import os
from pathlib import Path

import pytest

from evidence import compose_project_name, new_run_id, write_run_identity

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return ROOT


@pytest.fixture
def run_identity() -> dict:
    run_id = os.environ.get("AIDSPM_RUN_ID") or new_run_id()
    write_run_identity(run_id, os.environ.get("AIDSPM_CHECK", "verify-harness"))
    return {
        "run_id": run_id,
        "compose_project": compose_project_name(run_id),
        "compose_started": False,
    }