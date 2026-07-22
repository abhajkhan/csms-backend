"""Attendance ORM model.

Table: ``attendances``
Design reference: Construction_System_Design_v2.md §4.5

Polymorphic attendance: ``labour_type`` + ``labour_id`` reference
either ``users`` or ``workers`` without a hard FK constraint.

``site_id`` is nullable because drivers are not assigned to a
specific site.

``is_verified`` is nullable — it is only meaningful for supervisor
attendance records (app layer sets a default of ``False`` for
supervisors; workers/drivers leave it ``NULL``).

Business rule: if admin sets ``is_verified=False`` on a supervisor
attendance record, all ``Expense`` records by that supervisor for
that date must be deleted atomically.
"""

from __future__ import annotations

from datetime import date as date_type, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.site import Site
    from app.models.user import User


class Attendance(Base):
    """Daily attendance record for a user or worker.

    Attributes
    ----------
    attendance_id : int
        Primary key, auto-incremented.
    date : date
        Calendar date of the attendance record.
    labour_type : str
        Discriminator — ``'USER'`` or ``'WORKER'``
        (``LabourType`` enum stored as VARCHAR).
    labour_id : int
        References ``users.user_id`` or ``workers.worker_id``
        depending on ``labour_type`` (no FK constraint).
    site_id : int | None
        FK → ``sites.site_id``; ``NULL`` for driver records.
    status : str
        ``'present'``, ``'absent'``, or ``'half_day'``
        (``AttendanceStatus`` enum stored as VARCHAR).
    is_verified : bool | None
        Verification flag for supervisor attendance.
        ``NULL`` for workers and drivers.
    verified_by : int | None
        FK → ``users.user_id``; admin who verified.
    verified_at : datetime | None
        Timestamp of verification.
    """

    __tablename__ = "attendances"

    __table_args__ = (
        UniqueConstraint(
            "labour_type",
            "labour_id",
            "site_id",
            "date",
            name="uq_attendance_unique",
        ),
        Index("ix_attendance_date", "date"),
        Index(
            "ix_attendance_labour",
            "labour_type",
            "labour_id",
        ),
    )

    attendance_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    date: Mapped[date_type] = mapped_column(
        Date,
        nullable=False,
    )
    labour_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    labour_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    site_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("sites.site_id"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        server_default="present",
    )
    is_verified: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
    )
    verified_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=True,
    )
    verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ── Relationships ─────────────────────────────────────────

    site: Mapped[Site | None] = relationship(
        "Site",
        back_populates="attendances",
    )
    verified_by_user: Mapped[User | None] = relationship(
        "User",
        back_populates="verified_attendances",
        foreign_keys=[verified_by],
    )
