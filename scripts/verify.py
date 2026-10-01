"""Capability verification runner. Empty collection is not a pass."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from evidence import (
    compose_project_name,
    new_run_id,
    write_manifest,
    write_run_identity,
)

PASS, FAIL, UNIMPLEMENTED, MISSING = 0, 1, 2, 3
REGISTRY = ROOT / "tests" / "task_registry.yaml"


def load_registry() -> dict:
    """Load the registry from the file.
    
    Returns:
        The registry.
    """
    return yaml.safe_load(REGISTRY.read_text())


def run(cmd: list[str], env: dict | None = None) -> subprocess.CompletedProcess[str]:
    """Run a command.
    
    Args:
        cmd: The command to run.
        env: The environment variables to set.

    Returns:
        The completed process.
    """
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, env=env, check=False)



def pytest_status(selectors: list[str], extra: list[str] | None = None) -> int:
    """Run pytest and return the status.
    
    Args:
        selectors: The selectors to run.
        extra: The extra arguments to pass to pytest.

    Returns:
        The status.
    """
    if not selectors:
        return UNIMPLEMENTED
    cmd = ["uv", "run", "--python", "3.12", "pytest", "-q", *selectors, *(extra or [])]
    proc = run(cmd)
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    if proc.returncode == 0:
        return PASS
    if proc.returncode == 5:
        return UNIMPLEMENTED
    return FAIL

def check_required_files(files: list[str]) -> int:
    """Check if the required files are present.
    
    Args:
        files: The files to check.

    Returns:
        The status.
    """
    missing = [f for f in files if not (ROOT / f).is_file()]
    if missing:
        print("MISSING_EVIDENCE")
        for item in missing:
            print(f"- {item}")
        return MISSING
    return PASS


def verify_product_contract() -> int:
    """
    Verify the product contract by running a Python script that checks the scope.json and the mvp.md files.

    This script is used to verify that the product contract is correct and that the required files are present.
    It checks that the schema_version, product, processing_boundary, and nine_questions are present and that the nine_questions are exactly 9.
    It also checks that the text does not contain any TODO, TBD, FIXME, or CHANGEME.

    Returns:
        The status.
    """
    script = r"""
import json, pathlib, re, sys
root = pathlib.Path(".")
scope = json.loads((root/"docs/scope.json").read_text())
required = ["schema_version","product","processing_boundary","nine_questions"]
missing = [k for k in required if k not in scope]
assert not missing, missing
assert len(scope["nine_questions"]) == 9
text = (root/"docs/scope.json").read_text() + (root/"docs/capabilities/mvp.md").read_text()
assert not re.search(r"\b(TODO|TBD|FIXME|CHANGEME)\b", text)
print("PRODUCT_CONTRACT_OK")
"""
    proc = run(["uv", "run", "--python", "3.12", "python", "-c", script])
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    return PASS if proc.returncode == 0 else FAIL



def verify_check(name: str) -> int:
    """Verify a check - this is the main entry point for the verification process.
    It loads the registry, checks if the check is implemented, checks if the required files are present,
    and then runs the appropriate verification function.
    """
    registry = load_registry()
    checks = registry["checks"]
    if name not in checks:
        print(f"unknown check: {name}")
        return UNIMPLEMENTED
    spec = checks[name]
    if spec.get("status") == "unimplemented":
        print(f"UNIMPLEMENTED {name}")
        return UNIMPLEMENTED
    files_status = check_required_files(spec.get("required_files") or [])
    if files_status != PASS:
        return files_status
    if name == "product-contract":
        return verify_product_contract()
    if name == "toolchain":
        command = spec.get("command") or "make doctor"
        proc = run(["bash", "-lc", command])
        sys.stdout.write(proc.stdout)
        sys.stderr.write(proc.stderr)
        return PASS if proc.returncode == 0 else FAIL
    if name == "first-live-stack":
        from live_stack import prove

        return PASS if prove() == 0 else FAIL
    if name == "verify-harness":
        return pytest_status(spec["pytest_selectors"])
    selectors = spec.get("pytest_selectors") or []
    if not selectors:
        print(f"UNIMPLEMENTED {name} (no selectors)")
        return UNIMPLEMENTED
    return pytest_status(selectors)




def cmd_verify(check: str) -> int:
    """
    cmd_verify differs from verify_check in that it generates a new run ID, writes the run identity,
    verifies the check, writes the manifest, and prints the run ID and evidence path.
    This is the main entry point for the verification process.
    """
    run_id = new_run_id()
    write_run_identity(run_id, check)
    code = verify_check(check)
    dest = ROOT / "artifacts" / check / run_id
    write_manifest(
        dest,
        {
            "check": check,
            "run_id": run_id,
            "compose_project": compose_project_name(run_id),
            "compose_started": False,
            "exit_code": code,
            "status": {0: "pass", 1: "fail", 2: "unimplemented", 3: "missing"}[code],
            "frontend": "not_applicable",
            "dirty_hint": "see git status in operator notes; do not copy secrets",
        },
    )
    print(f"RUN_ID={run_id}")
    print(f"EVIDENCE={dest}")
    return code



def phase_checks(phase: str) -> tuple[list[str], list[str]]:
    """Return runnable names and unimplemented names for a phase."""
    registry = load_registry()
    runnable: list[str] = []
    pending: list[str] = []
    for name, spec in registry["checks"].items():
        if spec.get("phase") != phase:
            continue
        if spec.get("status") == "runnable":
            runnable.append(name)
        else:
            pending.append(name)
    return runnable, pending


def cmd_gate(phase: str) -> int:
    """Run every runnable check. Unimplemented checks in the phase are not a pass."""
    runnable, pending = phase_checks(phase)
    if not runnable and not pending:
        print(f"no checks in phase {phase}")
        return UNIMPLEMENTED
    for name in pending:
        print(f"INCOMPLETE {name}")
    worst = PASS
    for name in runnable:
        print(f"== {name} ==")
        code = cmd_verify(name)
        if code == FAIL:
            return FAIL
        if code != PASS:
            worst = code
    if pending:
        return UNIMPLEMENTED
    return worst


def main() -> int:

    parser = argparse.ArgumentParser()
    parser.add_argument("--check") #verify a specific check
    parser.add_argument("--gate-phase") #run all the checks in a given phase
    parser.add_argument("--sentinel", choices=["pass", "fail", "empty"]) #run a sentinel check
    args = parser.parse_args()
    if args.sentinel: #run a sentinel check
        registry = load_registry()
        return pytest_status(registry["sentinels"][args.sentinel]["pytest_selectors"]) #run a sentinel check
    if args.gate_phase:
        return cmd_gate(args.gate_phase) #run all the checks in a given phase
    if not args.check:
        print("usage: --check <slug> | --gate-phase <phase> | --sentinel pass|fail|empty")
        return FAIL
    return cmd_verify(args.check)


if __name__ == "__main__":
    sys.exit(main())
