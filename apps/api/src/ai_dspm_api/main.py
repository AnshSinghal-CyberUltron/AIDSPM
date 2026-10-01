"""Process entrypoint for the G0 operator API."""

from __future__ import annotations

import os
import uuid
from datetime import UTC, datetime

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from ai_dspm_api.db import connect, database_dsn

app = FastAPI(title="ZeroShield AI DSPM Operator API", version="0.1.0")


def _request_id() -> str:
    return str(uuid.uuid4())


def _unavailable(message: str) -> JSONResponse:
    body = {
        "error": {
            "code": "UNAVAILABLE",
            "message": message,
            "request_id": _request_id(),
        }
    }
    return JSONResponse(status_code=503, content=body)


def _ready() -> bool:
    if not database_dsn():
        return False
    try:
        with connect() as conn:
            conn.execute(text("SELECT 1"))
            row = conn.execute(text("SELECT installation_id FROM installation LIMIT 1")).first()
        return row is not None
    except SQLAlchemyError:
        return False


@app.get("/livez")
def livez() -> dict[str, str]:
    return {"status": "alive"}


@app.get("/readyz", response_model=None)
def readyz() -> JSONResponse | dict[str, str]:
    if not _ready():
        return _unavailable("database unavailable")
    return {"status": "ready"}


@app.get("/api/v1/system", response_model=None)
def system() -> JSONResponse | dict[str, str]:
    if not database_dsn():
        return _unavailable("database unavailable")
    try:
        with connect() as conn:
            row = conn.execute(
                text("SELECT installation_id::text FROM installation LIMIT 1"),
            ).first()
    except SQLAlchemyError:
        return _unavailable("database unavailable")
    if row is None:
        return _unavailable("installation record missing")
    return {
        "installation_id": row[0],
        "build_revision": os.environ.get("AIDSPM_BUILD_REVISION", "dev"),
        "server_time": datetime.now(UTC).isoformat(),
        "database": "ready",
    }
