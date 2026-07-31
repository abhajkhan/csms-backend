"""Attendance ORM model.

Table: ``attendances``
Design reference: CSMS_SPEC.md §6.5

Polymorphic attendance: ``labour_type`` + ``labour_id`` reference
either ``users`` or ``workers`` without a hard FK constraint.

``site_id`` is nullable because drivers are not assigned to a
specific site.
"""

from __future__ import annotations

from datetime import date as date_type
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
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

    # ── Relationships ─────────────────────────────────────────

    site: Mapped[Site | None] = relationship(
        "Site",
        back_populates="attendances",
    )
