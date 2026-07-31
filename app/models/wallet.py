"""SupervisorBalanceLog ORM model — supervisor balance ledger.

Table: ``supervisor_balance_logs``
Design reference: CSMS_SPEC.md §6.6
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class SupervisorBalanceLog(Base):
    """Immutable ledger row for a supervisor wallet transaction.

    Design ref: CSMS_SPEC.md §6.6
    """

    __tablename__ = "supervisor_balance_logs"
    __table_args__ = (
        Index("ix_balance_log_supervisor", "supervisor_id"),
    )

    log_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    supervisor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
    )
    txn_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        doc="TxnType enum value: 'credit' | 'debit'",
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    note: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ── Relationships ────────────────────────────────────────────
    supervisor: Mapped[User] = relationship(
        "User",
        back_populates="balance_logs",
        foreign_keys=[supervisor_id],
    )
