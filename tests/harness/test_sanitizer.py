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