"""Worker ORM model.

Table: ``workers``
Design reference: CSMS_SPEC.md §6.4

Workers are casual labourers hired per-site.  Each record tracks
the worker's name, daily wage, and the user who created them.
``is_active`` acts as a soft-delete flag.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.worker_payment import WorkerPayment


class Worker(Base):
    """A casual worker employed on construction sites.

    Attributes
    ----------
    worker_id : int
        Primary key, auto-incremented.
    full_name : str
        Display name of the worker.
    daily_wage : Decimal
        Wage paid per working day (₹).
    is_active : bool
        ``False`` marks the worker as soft-deleted.
    created_by : int
        FK → ``users.user_id``; the admin or supervisor who
        registered this worker.
    """

    __tablename__ = "workers"

    worker_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    daily_wage: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
    )
    created_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────

    created_by_user: Mapped[User] = relationship(
        "User",
        back_populates="created_workers",
        foreign_keys=[created_by],
    )
    payments: Mapped[list[WorkerPayment]] = relationship(
        "WorkerPayment",
        back_populates="worker",
    )
