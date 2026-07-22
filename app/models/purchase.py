"""Purchase ORM model.

Table: ``purchases`` (§4.15)

Records every material purchase made by a normal driver.  Each row
captures who bought what, from where, the destination (site or
warehouse), vehicle details, and pricing.

Auto-creates related ``Expense`` entries for driver_material,
driver_bata (own vehicle), and driver_vehicle_rent (outer vehicle).

Design reference: Construction_System_Design_v2.md §4.15.
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
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.site import Site
    from app.models.user import User
    from app.models.warehouse import Warehouse, WarehouseItem


class Purchase(Base):
    """A material purchase performed by a normal driver.

    ``destination_type`` stores a :pyclass:`DestinationType` enum
    value as VARCHAR — either ``'site'`` or ``'warehouse'``.

    ``vehicle_type`` stores a :pyclass:`VehicleType` enum value as
    VARCHAR — one of ``'own'``, ``'outer'``, ``'none'``.

    When ``destination_type == 'site'``, ``site_id`` is populated
    and ``warehouse_id`` is NULL; the reverse applies for
    ``'warehouse'`` destinations.
    """

    __tablename__ = "purchases"
    __table_args__ = (
        Index("ix_purchase_date", "purchase_date"),
        Index("ix_purchase_driver", "purchased_by"),
    )

    purchase_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    purchased_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
    )
    item_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("warehouse_items.item_id"),
        nullable=False,
    )
    site_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("sites.site_id"),
        nullable=True,
        comment="NULL when destination_type='warehouse'",
    )
    warehouse_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("warehouses.warehouse_id"),
        nullable=True,
        comment="NULL when destination_type='site'",
    )
    destination_type: Mapped[str] = mapped_column(
        String(15),
        nullable=False,
        comment="DestinationType enum: site | warehouse",
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
    unit: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    purchased_from: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )
    vehicle_type: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="VehicleType enum: own | outer | none",
    )
    vehicle_rent: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )
    purchase_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    note: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ── relationships ────────────────────────────────────────
    purchased_by_user: Mapped[User] = relationship(
        back_populates="purchases",
        foreign_keys=[purchased_by],
    )
    item: Mapped[WarehouseItem] = relationship(
        back_populates="purchases",
    )
    site: Mapped[Site | None] = relationship(
        back_populates="purchases",
    )
    warehouse: Mapped[Warehouse | None] = relationship(
        back_populates="purchases",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Purchase id={self.purchase_id!r} "
            f"by={self.purchased_by!r} "
            f"item={self.item_id!r} "
            f"dest={self.destination_type!r}>"
        )
