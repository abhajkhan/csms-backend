"""StockMovement ORM model.

Table: ``stock_movements``
Design reference: CSMS_SPEC.md §6.14
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
    from app.models.site import Site
    from app.models.warehouse import Warehouse, WarehouseItem


class StockMovement(Base):
    """Single IN or OUT movement of a warehouse item.

    OUT movements populate ``site_id`` (the destination site) and
    auto-create an ``Expense`` row via service-layer logic.

    Design ref: CSMS_SPEC.md §6.14
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
