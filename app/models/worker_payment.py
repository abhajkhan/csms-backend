"""WorkerPayment ORM model.

Table: ``worker_payments``
Design reference: CSMS_SPEC.md §6.7
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


class WorkerPayment(Base):
    """Payment record — advance or settlement — for a worker.

    Design ref: CSMS_SPEC.md §6.7
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
