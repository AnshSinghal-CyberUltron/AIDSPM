"""
Sanitizer tests. Tests that the sanitizer redacts canary emails and bearer tokens.

Args:
    text: The text to sanitize.

Returns:
    The sanitized text.
"""

from pathlib import Path

from evidence import sanitize_text


def test_redacts_canary_email() -> None:
    text = "user alice.hr@example.com saw payroll-canary-128000"
    out = sanitize_text(text)
    assert "alice.hr@example.com" not in out
    assert "payroll-canary-128000" not in out
    assert "[CANARY]" in out


def test_redacts_bearer_token() -> None:
    out = sanitize_text("Authorization: Bearer super-secret-token")
    assert "super-secret-token" not in out
    assert "[REDACTED]" in out


def test_basic_and_sqlalchemy_dsn_do_not_survive() -> None:
    text = (
        "Authorization: Basic dXNlcjpwYXNz "
        "CATALOG_DATABASE_DSN=postgresql+psycopg://user:pass@catalog:5432/aidspm"
    )
    out = sanitize_text(text)
    assert "dXNlcjpwYXNz" not in out
    assert "user:pass" not in out
    assert "postgresql+psycopg://" not in out


def test_shareable_fields_drop_secrets() -> None:
    from evidence import shareable_fields

    kept = shareable_fields(
        {
            "check": "first-live-stack",
            "status": "pass",
            "CATALOG_DATABASE_DSN": "postgresql+psycopg://user:pass@db/app",
            "Authorization": "Basic dXNlcjpwYXNz",
        }
    )
    assert kept == {"check": "first-live-stack", "status": "pass"}


def test_run_ids_are_unique_within_the_same_second() -> None:
    from evidence import new_run_id

    assert new_run_id() != new_run_id()