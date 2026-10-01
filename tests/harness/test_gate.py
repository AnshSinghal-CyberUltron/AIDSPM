"""Foundations gate must not pass while required checks are unimplemented."""

from verify import phase_checks


def test_foundations_still_reports_unimplemented_checks() -> None:
    _runnable, pending = phase_checks("foundations")
    assert "first-live-stack" not in pending
    assert "catalog-tenant-isolation" in pending
