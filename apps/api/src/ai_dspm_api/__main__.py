"""Create the installation row, then serve the API."""

from __future__ import annotations

import uvicorn

from ai_dspm_api.db import ensure_installation
from ai_dspm_api.main import app


def main() -> None:
    ensure_installation()
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
