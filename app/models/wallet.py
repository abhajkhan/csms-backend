"""Wallet ORM models — supervisor balance ledger & worker payments.

Tables
------
``supervisor_balance_logs``  (§4.6)
    Immutable ledger of every credit / debit applied to a supervisor's
    ``acc_balance``.  Every update to ``users.acc_balance`` **must** produce
    a corresponding ``SupervisorBalanceLog`` row in the same transaction.

``worker_payments``  (§4.7)
    Records every advance or settlement paid to a worker.
    ``paid_by`` links to the user (supervisor for advances, admin for
    settlements) who initiated the payment.

Design reference: Construction_System_Design_v2.md §4.6, §4.7
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
    from app.models.worker import Worker


class SupervisorBalanceLog(Base):
    """Immutable ledger row for a supervisor wallet transaction.

    Design ref: Construction_System_Design_v2.md §4.6
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


class WorkerPayment(Base):
    """Payment record — advance or settlement — for a worker.

    Design ref: Construction_System_Design_v2.md §4.7
    """

    __tablename__ = "worker_payments"
    __table_args__ = (
        Index("ix_worker_payment_worker", "worker_id"),
        Index("ix_worker_payment_paid_at", "paid_at"),
    )

    payment_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    worker_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("workers.worker_id"),
        nullable=False,
    )
    paid_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    payment_type: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
        doc=(
            "PaymentType enum value: "
            "'advance' | 'settlement'"
        ),
    )
    paid_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    note: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # ── Relationships ────────────────────────────────────────────
    worker: Mapped[Worker] = relationship(
        "Worker",
        back_populates="payments",
        foreign_keys=[worker_id],
    )
    paid_by_user: Mapped[User] = relationship(
        "User",
        back_populates="worker_payments",
        foreign_keys=[paid_by],
    )
