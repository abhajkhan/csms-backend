"""Expense ORM model — unified expense ledger.

Table: ``expenses``  (§4.8)
    Central record for every expense incurred on a site.  Rows are
    auto-created by service-layer logic when an ``AjaxDriverLog``,
    ``HitachiDriverLog``, ``StockMovement`` (OUT), or ``Purchase``
    is persisted.

    The ``reference_id`` / ``reference_type`` pair forms a polymorphic
    link back to the originating record, enabling drill-down from the
    expense ledger into the source domain table.

Design reference: Construction_System_Design_v2.md §4.8
"""

from __future__ import annotations

from datetime import date as date_type
from datetime import datetime
from decimal import Decimal

from typing import TYPE_CHECKING

from sqlalchemy import (
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.ajax_driver_log import AjaxDriverLog
    from app.models.hitachi_driver_log import HitachiDriverLog
    from app.models.site import Site
    from app.models.user import User


class Expense(Base):
    """Single expense entry linked to a site.

    Design ref: Construction_System_Design_v2.md §4.8
    """

    __tablename__ = "expenses"
    __table_args__ = (
        Index("ix_expense_site_date", "site_id", "date"),
        Index("ix_expense_type", "expense_type"),
        Index("ix_expense_recorded_by", "recorded_by"),
    )

    expense_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    date: Mapped[date_type] = mapped_column(
        Date,
        nullable=False,
    )
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    site_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sites.site_id"),
        nullable=False,
    )
    recorded_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
    )
    expense_type: Mapped[str] = mapped_column(
        String(25),
        nullable=False,
        doc="ExpenseType enum value",
    )
    reference_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        doc="Polymorphic FK to the source record",
    )
    reference_type: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        doc="ReferenceType enum value",
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ── Relationships ────────────────────────────────────────────
    site: Mapped[Site] = relationship(
        "Site",
        back_populates="expenses",
    )
    recorded_by_user: Mapped[User] = relationship(
        "User",
        back_populates="recorded_expenses",
        foreign_keys=[recorded_by],
    )
    ajax_log: Mapped[AjaxDriverLog | None] = relationship(
        "AjaxDriverLog",
        back_populates="expense",
        uselist=False,
    )
    hitachi_log: Mapped[
        HitachiDriverLog | None
    ] = relationship(
        "HitachiDriverLog",
        back_populates="expense",
        uselist=False,
    )
