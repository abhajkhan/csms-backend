"""Stock & driver-log ORM models.

Tables
------
``ajax_driver_logs``    (§4.9)
    Daily log for Ajax mixer drivers — number of mixes × rate.

``hitachi_driver_logs`` (§4.10)
    Daily log for Hitachi excavator drivers — hours × hourly rate.

``stock_movements``     (§4.14)
    IN/OUT movements of warehouse inventory.  OUT movements
    auto-create an ``Expense`` row via service-layer logic.

Design reference: Construction_System_Design_v2.md §4.9, §4.10, §4.14
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
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.expense import Expense
    from app.models.site import Site
    from app.models.user import User
    from app.models.warehouse import Warehouse, WarehouseItem


class AjaxDriverLog(Base):
    """Daily Ajax mixer driver log entry.

    Auto-creates a linked ``Expense`` row on save
    (``expense_type='ajax_service'``).

    Design ref: Construction_System_Design_v2.md §4.9
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


class HitachiDriverLog(Base):
    """Daily Hitachi excavator driver log entry.

    Auto-creates a linked ``Expense`` row on save
    (``expense_type='hitachi_service'``).

    Design ref: Construction_System_Design_v2.md §4.10
    """

    __tablename__ = "hitachi_driver_logs"
    __table_args__ = (
        Index(
            "ix_hitachi_log_driver_date",
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
    hours_worked: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    hourly_rate: Mapped[Decimal] = mapped_column(
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
        back_populates="hitachi_logs",
        foreign_keys=[driver_id],
    )
    site: Mapped[Site] = relationship(
        "Site",
        back_populates="hitachi_logs",
    )
    expense: Mapped[Expense | None] = relationship(
        "Expense",
        back_populates="hitachi_log",
        foreign_keys=[expense_id],
    )


class StockMovement(Base):
    """Single IN or OUT movement of a warehouse item.

    OUT movements populate ``site_id`` (the destination site) and
    auto-create an ``Expense`` row via service-layer logic.

    Design ref: Construction_System_Design_v2.md §4.14
    """

    __tablename__ = "stock_movements"
    __table_args__ = (
        Index(
            "ix_stock_movement_warehouse",
            "warehouse_id",
        ),
        Index(
            "ix_stock_movement_date",
            "movement_date",
        ),
    )

    movement_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    warehouse_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("warehouses.warehouse_id"),
        nullable=False,
    )
    item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("warehouse_items.item_id"),
        nullable=False,
    )
    movement_type: Mapped[str] = mapped_column(
        String(5),
        nullable=False,
        doc="MovementType enum value: 'IN' | 'OUT'",
    )
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    movement_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    site_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("sites.site_id"),
        nullable=True,
        doc="Populated for OUT movements",
    )
    reference: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    created_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
    )

    # ── Relationships ────────────────────────────────────────────
    warehouse: Mapped[Warehouse] = relationship(
        "Warehouse",
        back_populates="stock_movements",
    )
    item: Mapped[WarehouseItem] = relationship(
        "WarehouseItem",
        back_populates="stock_movements",
    )
    site: Mapped[Site | None] = relationship(
        "Site",
        back_populates="stock_movements",
    )


# WarehouseStock is in warehouse.py
