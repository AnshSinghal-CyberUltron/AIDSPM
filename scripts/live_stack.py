"""Bring up catalog, API, and web, then check the System contract."""

from __future__ import annotations

import json
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "ops" / "compose" / "compose.yml"


def _compose(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["docker", "compose", "--env-file", str(ROOT / ".env"), "-f", str(COMPOSE), *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _get(url: str) -> tuple[int, str]:
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8", errors="replace")


def prove() -> int:
    up = _compose("up", "-d", "--build", "catalog", "api", "web")
    if up.returncode != 0:
        print(up.stdout)
        print(up.stderr)
        print("LIVE_STACK_FAIL compose")
        return 1
    deadline = time.monotonic() + 180
    body = ""
    while time.monotonic() < deadline:
        status, body = _get("http://127.0.0.1:8000/api/v1/system")
        if status == 200:
            break
        time.sleep(2)
    else:
        print(body)
        print("LIVE_STACK_FAIL system")
        return 1
    payload = json.loads(body)
    if payload.get("database") != "ready" or not payload.get("installation_id"):
        print("LIVE_STACK_FAIL system-shape")
        return 1
    ready_status, ready_body = _get("http://127.0.0.1:8000/readyz")
    if ready_status != 200 or json.loads(ready_body).get("status") != "ready":
        print("LIVE_STACK_FAIL readyz")
        return 1
    live_status, live_body = _get("http://127.0.0.1:8000/livez")
    if live_status != 200 or json.loads(live_body).get("status") != "alive":
        print("LIVE_STACK_FAIL livez")
        return 1
    page_status, page = _get("http://127.0.0.1:5173/")
    if page_status != 200 or "AI DSPM" not in page:
        print("LIVE_STACK_FAIL web")
        return 1
    print("LIVE_STACK_OK")
    print(f"installation_id={payload['installation_id']}")
    return 0
