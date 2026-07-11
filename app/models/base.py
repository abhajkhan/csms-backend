"""Shared model infrastructure.

Provides:
    ``TimestampMixin``  — adds ``created_at`` / ``updated_at`` columns.

Individual models define their own primary key column (named per the system
design, e.g. ``user_id``, ``site_id``) rather than using a generic ``id``
from a base class.
"""

from sqlalchemy import Column, DateTime, func

from app.db.base import Base


class TimestampMixin:
    """Adds ``created_at`` and ``updated_at`` audit timestamp columns."""

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )


__all__ = ["Base", "TimestampMixin"]
