"""AjaxDriverLog ORM model.

Table: ``ajax_driver_logs``
Design reference: CSMS_SPEC.md §6.9
"""

from __future__ import annotations

from datetime import date as date_type
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.expense import Expense
    from app.models.site import Site
    from app.models.user import User


class AjaxDriverLog(Base):
    """Daily Ajax mixer driver log entry.

    Auto-creates a linked ``Expense`` row on save
    (``expense_type='ajax_service'``).

    Design ref: CSMS_SPEC.md §6.9
    """

    __tablename__ = "ajax_driver_logs"
    __table_args__ = (
        Index(
            "ix_ajax_log_driver_date",
            "driver_id",
            "date",
        ),
    )

    log_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    driver_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
    )
    site_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sites.site_id"),
        nullable=False,
    )
    date: Mapped[date_type] = mapped_column(
        Date,
        nullable=False,
    )
    num_mixes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    rate_per_mix: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    expense_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("expenses.expense_id"),
        nullable=True,
        doc="Auto-created on save",
    )
    note: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # ── Relationships ────────────────────────────────────────────
    driver: Mapped[User] = relationship(
        "User",
        back_populates="ajax_logs",
        foreign_keys=[driver_id],
    )
    site: Mapped[Site] = relationship(
        "Site",
        back_populates="ajax_logs",
    )
    expense: Mapped[Expense | None] = relationship(
        "Expense",
        back_populates="ajax_log",
        foreign_keys=[expense_id],
    )
