"""Shareable evidence keeps known fields. Text redaction is not a general scrubber."""

from __future__ import annotations

import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANARY_FILE = ROOT / "fixtures" / "redaction-canaries.txt"

SAFE_FIELDS = frozenset(
    {
        "run_id",
        "check",
        "compose_project",
        "compose_started",
        "created_at_utc",
        "exit_code",
        "status",
        "frontend",
        "dirty_hint",
        "installation_id",
        "database",
        "build_revision",
    }
)

TOKEN_RE = re.compile(
    r"(?i)("
    r"bearer\s+\S+"
    r"|authorization:\s*basic\s+\S+"
    r"|postgres(?:ql)?(?:\+[a-z0-9]+)?://\S+"
    r"|sk_live_[a-z0-9]+"
    r"|ghp_[a-z0-9]+"
    r")"
)


def load_canaries() -> list[str]:
    if not CANARY_FILE.is_file():
        return []
    values = []
    for line in CANARY_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            values.append(line)
    return values


def sanitize_text(text: str, extra: list[str] | None = None) -> str:
    redacted = TOKEN_RE.sub("[REDACTED]", text)
    for value in load_canaries() + (extra or []):
        if value:
            redacted = redacted.replace(value, "[CANARY]")
    return redacted


def shareable_fields(payload: dict[str, object]) -> dict[str, object]:
    """Drop every key that is not on the shareable allowlist."""
    return {key: payload[key] for key in payload if key in SAFE_FIELDS}


def copy_sanitized(src: Path, dst: Path) -> str:
    dst.parent.mkdir(parents=True, exist_ok=True)
    raw = src.read_text(encoding="utf-8", errors="replace")
    dst.write_text(sanitize_text(raw), encoding="utf-8")
    return hashlib.sha256(dst.read_bytes()).hexdigest()


def new_run_id() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y%m%dT%H%M%S") + f"{now.microsecond:06d}Z-" + uuid.uuid4().hex[:8]


def compose_project_name(run_id: str) -> str:
    safe = re.sub(r"[^a-z0-9-]", "", run_id.lower())
    return f"aidspm-test-{safe}"[:63]


def write_run_identity(run_id: str, check: str) -> Path:
    run_dir = ROOT / "artifacts" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    identity = shareable_fields(
        {
            "run_id": run_id,
            "check": check,
            "compose_project": compose_project_name(run_id),
            "compose_started": False,
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
        }
    )
    (run_dir / "compose-project.json").write_text(json.dumps(identity, indent=2) + "\n")
    return run_dir


def write_manifest(dest_dir: Path, payload: dict[str, object]) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    path = dest_dir / "manifest.json"
    safe = shareable_fields(payload)
    path.write_text(json.dumps(safe, indent=2, sort_keys=True) + "\n")
    return path


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()
