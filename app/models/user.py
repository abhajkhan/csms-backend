"""User model — maps to the ``users`` table (§4.1).

Stores admin, supervisor, and driver accounts.  The ``role``
column discriminates between the three user types while
``driver_type`` is only populated for driver accounts.
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.attendance import Attendance
    from app.models.expense import Expense
    from app.models.purchase import Purchase
    from app.models.site import Site, SiteSupervisor
    from app.models.stock import AjaxDriverLog, HitachiDriverLog
    from app.models.wallet import SupervisorBalanceLog, WorkerPayment
    from app.models.worker import Worker


class User(Base):
    """ORM model for the ``users`` table.

    Attributes
    ----------
    user_id : int
        Auto-incrementing primary key.
    role : str
        One of the ``UserRole`` enum values
        (``'admin'``, ``'supervisor'``, ``'driver'``).
    driver_type : str | None
        One of the ``DriverType`` enum values
        (``'hitachi'``, ``'ajax'``, ``'normal'``).
        ``None`` for admin / supervisor accounts.
    full_name : str
        Display name of the user.
    phone : str
        Unique phone number used as the login identifier.
    password_hash : str
        Hashed password.
    is_active : bool
        Soft-delete flag; ``False`` means logically deleted.
    acc_balance : Decimal | None
        Wallet balance for supervisors; ``None`` for others.
    """

    __tablename__ = "users"

    # ── primary key ───────────────────────────────────────
    user_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # ── core columns ──────────────────────────────────────
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    driver_type: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    full_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    phone: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    acc_balance: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    # ── relationships ─────────────────────────────────────
    site_assignments: Mapped[list["SiteSupervisor"]] = (
        relationship(
            back_populates="supervisor",
            lazy="selectin",
        )
    )
    created_sites: Mapped[list["Site"]] = relationship(
        back_populates="created_by_user",
        lazy="selectin",
    )
    created_workers: Mapped[list["Worker"]] = relationship(
        back_populates="created_by_user",
        lazy="selectin",
    )
    balance_logs: Mapped[list["SupervisorBalanceLog"]] = (
        relationship(
            back_populates="supervisor",
            lazy="selectin",
        )
    )
    worker_payments: Mapped[list["WorkerPayment"]] = (
        relationship(
            back_populates="paid_by_user",
            lazy="selectin",
        )
    )
    recorded_expenses: Mapped[list["Expense"]] = (
        relationship(
            back_populates="recorded_by_user",
            lazy="selectin",
        )
    )
    ajax_logs: Mapped[list["AjaxDriverLog"]] = relationship(
        back_populates="driver",
        lazy="selectin",
    )
    hitachi_logs: Mapped[list["HitachiDriverLog"]] = (
        relationship(
            back_populates="driver",
            lazy="selectin",
        )
    )
    purchases: Mapped[list["Purchase"]] = relationship(
        back_populates="purchased_by_user",
        lazy="selectin",
    )
    verified_attendances: Mapped[list["Attendance"]] = (
        relationship(
            back_populates="verified_by_user",
            lazy="selectin",
        )
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<User(user_id={self.user_id}, "
            f"role={self.role!r}, "
            f"phone={self.phone!r})>"
        )
