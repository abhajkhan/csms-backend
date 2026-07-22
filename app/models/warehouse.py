"""Warehouse & inventory ORM models.

Tables
------
- ``warehouses``        (§4.11) — physical storage locations.
- ``warehouse_items``   (§4.12) — catalogue of trackable materials.
- ``warehouse_stocks``  (§4.13) — per-warehouse item quantities.

Design reference: Construction_System_Design_v2.md §4.11–§4.13.
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
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.purchase import Purchase
    from app.models.stock import StockMovement


# ── §4.11 Warehouse ─────────────────────────────────────────────


class Warehouse(Base):
    """A physical warehouse that stores materials.

    Each warehouse tracks stock via :class:`WarehouseStock` rows
    and receives/dispatches items via :class:`StockMovement`.
    """

    __tablename__ = "warehouses"

    warehouse_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    location: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    # ── relationships ────────────────────────────────────────
    stock_entries: Mapped[list[WarehouseStock]] = relationship(
        back_populates="warehouse",
    )
    stock_movements: Mapped[list[StockMovement]] = relationship(
        back_populates="warehouse",
    )
    purchases: Mapped[list[Purchase]] = relationship(
        back_populates="warehouse",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Warehouse id={self.warehouse_id!r} "
            f"name={self.name!r}>"
        )


# ── §4.12 WarehouseItem ─────────────────────────────────────────


class WarehouseItem(Base):
    """Catalogue entry for a material tracked across warehouses.

    ``category`` stores an :pyclass:`ItemCategory` enum value as
    a plain VARCHAR string.  ``last_unit_price`` is refreshed on
    every purchase-IN transaction.
    """

    __tablename__ = "warehouse_items"

    item_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    category: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="ItemCategory enum value",
    )
    unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    last_unit_price: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
        comment="Updated on each purchase IN",
    )

    # ── relationships ────────────────────────────────────────
    stock_entries: Mapped[list[WarehouseStock]] = relationship(
        back_populates="item",
    )
    stock_movements: Mapped[list[StockMovement]] = relationship(
        back_populates="item",
    )
    purchases: Mapped[list[Purchase]] = relationship(
        back_populates="item",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<WarehouseItem id={self.item_id!r} "
            f"name={self.name!r}>"
        )


# ── §4.13 WarehouseStock ────────────────────────────────────────


class WarehouseStock(Base):
    """Current stock level of one item in one warehouse.

    The composite unique constraint on ``(warehouse_id, item_id)``
    guarantees at most one row per warehouse–item pair.
    ``last_updated`` is refreshed automatically on every UPDATE.
    """

    __tablename__ = "warehouse_stocks"
    __table_args__ = (
        UniqueConstraint(
            "warehouse_id",
            "item_id",
            name="uq_warehouse_stock_item",
        ),
        Index(
            "ix_warehouse_stock_wh_item",
            "warehouse_id",
            "item_id",
        ),
    )

    stock_id: Mapped[int] = mapped_column(
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
    quantity: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        server_default="0",
    )
    last_updated: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        onupdate=func.now(),
    )

    # ── relationships ────────────────────────────────────────
    warehouse: Mapped[Warehouse] = relationship(
        back_populates="stock_entries",
    )
    item: Mapped[WarehouseItem] = relationship(
        back_populates="stock_entries",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<WarehouseStock id={self.stock_id!r} "
            f"wh={self.warehouse_id!r} "
            f"item={self.item_id!r} "
            f"qty={self.quantity!r}>"
        )
