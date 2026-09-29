"""Fail closed if the local development toolchain is incomplete."""

from __future__ import annotations

import json
import os
import shutil
import socket
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS: list[str] = []
WARNINGS: list[str] = []


def run(cmd: list[str]) -> str:
    try:
        p = subprocess.run(cmd, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        return ""
    return (p.stdout or p.stderr or "").strip()


def need(ok: bool, msg: str) -> None:
    if not ok:
        ERRORS.append(msg)


def main() -> int:
    marker = ROOT / "ops" / "dev.marker"
    need(marker.is_file() and marker.read_text().strip() == "ai-dspm-test", "missing ops/dev.marker with ai-dspm-test")
    need((ROOT / "docs" / "scope.json").is_file(), "missing docs/scope.json")
    need(os.environ.get("AIDSPM_ENV", "dev") != "production", "refusing production context")

    need(shutil.which("docker") is not None, "docker missing")
    compose = run(["docker", "compose", "version"])
    need("version" in compose.lower() or "docker compose" in compose.lower(), "docker compose missing")

    need(shutil.which("uv") is not None, "uv missing")
    need(shutil.which("pnpm") is not None, "pnpm missing")
    need(shutil.which("node") is not None, "node missing")

    node = run(["node", "--version"])
    need(node.startswith("v24."), f"node major must be 24, got {node or 'missing'}")
    pnpm = run(["pnpm", "--version"])
    need(pnpm.startswith("12.4."), f"pnpm must be 12.4.x, got {pnpm or 'missing'}")

    py = run(["uv", "run", "--python", "3.12", "python", "--version"])
    need(py.startswith("Python 3.12."), f"python must be 3.12.x via uv, got {py or 'missing'}")

    arch = os.uname().machine
    need(arch in {"x86_64", "amd64", "aarch64", "arm64"}, f"unsupported architecture {arch}")

    st = os.statvfs("/")
    free_gib = (st.f_bavail * st.f_frsize) / (1024**3)
    need(free_gib >= 10, f"free disk {free_gib:.1f} GiB < 10 GiB")

    mem_bytes = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    mem_gib = mem_bytes / (1024**3)
    need(mem_gib >= 8, f"memory {mem_gib:.1f} GiB < 8 GiB")

    for port in (8000, 5173):
        s = socket.socket()
        s.settimeout(0.2)
        try:
            in_use = s.connect_ex(("127.0.0.1", port)) == 0
        finally:
            s.close()
        need(not in_use, f"port 127.0.0.1:{port} is in use")

    lock = json.loads((ROOT / "ops" / "images.lock.json").read_text())
    need("python" in lock["images"] and "node" in lock["images"], "images.lock.json incomplete")

    if ERRORS:
        print("DOCTOR_FAIL")
        for e in ERRORS:
            print(f"- {e}")
        return 1
    print("DOCTOR_OK")
    print(f"arch={arch} free_disk_gib={free_gib:.1f} mem_gib={mem_gib:.1f}")
    print(f"{py} | {node} | pnpm {pnpm}")
    return 0


if __name__ == "__main__":
    sys.exit(main())