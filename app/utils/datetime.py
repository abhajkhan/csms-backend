"""Date and time utilities for CSMS backend.

All datetime objects are **timezone-aware UTC** unless stated otherwise.
Never use ``datetime.utcnow()`` (deprecated) — use ``now_utc()`` instead.

Per 02_BACKEND_RULES.md §15 Date/Time Handling.
"""

from datetime import date, datetime, timezone


def now_utc() -> datetime:
    """Return the current UTC datetime (timezone-aware).

    Replaces the deprecated ``datetime.utcnow()``.

    Returns:
        Timezone-aware ``datetime`` in UTC.

    Example::

        recorded_at = now_utc()
    """
    return datetime.now(tz=timezone.utc)


def today_utc() -> date:
    """Return today's date in UTC.

    Returns:
        A ``datetime.date`` representing today in UTC.
    """
    return now_utc().date()


def date_to_datetime(d: date) -> datetime:
    """Convert a ``date`` to a midnight UTC-aware ``datetime``.

    Args:
        d: The date to convert.

    Returns:
        ``datetime`` at 00:00:00 UTC for the given date.
    """
    return datetime(d.year, d.month, d.day, tzinfo=timezone.utc)


def format_date(d: date) -> str:
    """Return an ISO-8601 date string (``YYYY-MM-DD``).

    Args:
        d: The date to format.

    Returns:
        A string in the format ``"2025-03-15"``.
    """
    return d.isoformat()


def format_datetime(dt: datetime) -> str:
    """Return an ISO-8601 datetime string with UTC offset.

    Args:
        dt: A timezone-aware ``datetime``.

    Returns:
        A string in the format ``"2025-03-15T10:30:00+00:00"``.
    """
    return dt.isoformat()
