"""
Test the exit codes of the runner.

Args:
    args: The arguments to pass to the runner.

Returns:
    The exit code of the runner.
"""


import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def invoke(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", "--python", "3.12", "python", "scripts/verify.py", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_unimplemented_check_is_exit_2() -> None:
    proc = invoke("--check", "protected-rag-gate")
    assert proc.returncode == 2, proc.stdout + proc.stderr


def test_pass_sentinel_is_exit_0() -> None:
    proc = invoke("--sentinel", "pass")
    assert proc.returncode == 0, proc.stdout + proc.stderr


def test_fail_sentinel_is_exit_1() -> None:
    proc = invoke("--sentinel", "fail")
    assert proc.returncode == 1, proc.stdout + proc.stderr


def test_empty_collection_is_exit_2() -> None:
    proc = invoke("--sentinel", "empty")
    assert proc.returncode == 2, proc.stdout + proc.stderr