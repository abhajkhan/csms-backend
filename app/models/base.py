"""Shared model infrastructure.

Provides:
    ``TimestampMixin``  — adds ``created_at`` / ``updated_at`` columns.

Individual models define their own primary key column (named per the system
design, e.g. ``user_id``, ``site_id``) rather than using a generic ``id``
from a base class.
"""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TimestampMixin:
    """Adds ``created_at`` and ``updated_at`` audit timestamp columns.

    ``created_at`` is set automatically on INSERT via server_default.
    ``updated_at`` is set automatically on UPDATE via onupdate.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
        default=None,
    )


__all__ = ["Base", "TimestampMixin"]
