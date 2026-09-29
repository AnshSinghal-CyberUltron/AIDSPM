"""Sanitize and hash evidence files. Never retain secrets or canary payloads."""

from __future__ import annotations

import hashlib #for hashing
from hmac import digest
import json #for json
from optparse import Values
import os #for using os
import re #for regex
import shutil #for copying files
from datetime import datetime, timezone #for timestamps
from pathlib import Path #for file paths

ROOT = Path(__file__).resolve().parents[1] #get the root directory
CANARY_FILE = ROOT / "fixtures" / "redaction-canaries.txt" #get the canary file - which has the secrets to be redacted
TOKEN_RE = re.compile(
    r"(?i)(bearer\s+[a-z0-9._\-]+|postgres(?:ql)?://\S+|sk_live_[a-z0-9]+|ghp_[a-z0-9]+)"
) #this is the regex for the tokens to be redacted like API keys, etc.


def load_canaries() -> list[str]:
    """Load the canary file and return a list of canaries."""
    if not CANARY_FILE.is_file():
        return []
    values = []
    for line in CANARY_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            values.append(line)
    return values


def sanitize_text(text: str, extra: list[str] | None = None) -> str:
    """Sanitize text by redacting sensitive information.
    
    Args:
        text: The text to sanitize.
        extra: A list of extra strings to redact.

    Returns:
        The sanitized text.
    """
    redacted = TOKEN_RE.sub("[REDACTED]", text)
    for value in load_canaries() + (extra or []):
        if value:
            redacted = redacted.replace(value, "[CANARY]")
    return redacted


def copy_sanitized(src: Path, dst: Path) -> str:
    """Copy a file and sanitize it.

    Args:
        src: The source file.
        dst: The destination file.

    Returns:
        The destination file.
    """
    dst.parent.mkdir(parents=True, exist_ok=True) #create the parent directory if it doesn't exist
    raw = src.read_text(encoding="utf-8", errors="replace") #read the file and replace any errors with a placeholder
    dst.write_text(sanitize_text(raw), encoding="utf-8") #write the sanitized text to the destination file
    digest = hashlib.sha256(dst.read_bytes()).hexdigest() #hash the destination file
    return digest


def new_run_id() -> str:
    """Generate a new run ID.
    
    Returns:
        The new run ID.
    """
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") #format the run ID as a timestamp


def compose_project_name(run_id: str) -> str:
    """Compose a project name.
    
    Args:
        run_id: The run ID.

    Returns:
        The project name.
    """
    return f"aidspm-test-{run_id.lower()}"


def write_run_identity(run_id: str, check: str) -> Path:
    """Write a run identity to a file.
    
    Args:
        run_id: The run ID.
        check: The check name.

    Returns:
        The run directory.
    """
    run_dir = ROOT / "artifacts" / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    identity = {
        "run_id": run_id,
        "check": check,
        "compose_project": compose_project_name(run_id),
        "compose_started": False,
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    (run_dir / "compose-project.json").write_text(json.dumps(identity, indent=2) + "\n")
    return run_dir

def write_manifest(dest_dir: Path, payload: dict) -> Path:
    """Write a manifest to a file.
    
    Args:
        dest_dir: The destination directory.
        payload: The payload to write.

    Returns:
        The manifest file.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    path = dest_dir / "manifest.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return path

def sha256_file(path: Path) -> str:
    """Calculate the SHA-256 hash of a file.
    
    Args:
        path: The path to the file.

    Returns:
        The SHA-256 hash.
    """
    return hashlib.sha256(path.read_bytes()).hexdigest()

