"""Catalog connection and the single installation row."""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection, Engine

_engine: Engine | None = None


def database_dsn() -> str:
    return os.environ.get("CATALOG_DATABASE_DSN", "").strip()


def engine() -> Engine:
    global _engine
    dsn = database_dsn()
    if not dsn:
        raise RuntimeError("CATALOG_DATABASE_DSN is unset")
    if _engine is None:
        _engine = create_engine(dsn, pool_pre_ping=True)
    return _engine


@contextmanager
def connect() -> Iterator[Connection]:
    with engine().begin() as conn:
        yield conn


def ensure_installation() -> None:
    with engine().begin() as conn:
        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS installation (
                    installation_id UUID PRIMARY KEY,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
                """
            )
        )
        conn.execute(
            text(
                """
                INSERT INTO installation (installation_id)
                SELECT gen_random_uuid()
                WHERE NOT EXISTS (SELECT 1 FROM installation)
                """
            )
        )
