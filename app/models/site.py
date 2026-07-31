"""Site models — ``sites`` (§4.2) and ``site_supervisors`` (§4.3).

``Site`` represents a physical construction site, while
``SiteSupervisor`` is the many-to-many association that links
supervisors (users with role ``'supervisor'``) to the sites
they manage.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.ajax_driver_log import AjaxDriverLog
    from app.models.attendance import Attendance
    from app.models.expense import Expense
    from app.models.hitachi_driver_log import HitachiDriverLog
    from app.models.purchase import Purchase
    from app.models.site_supervisor import SiteSupervisor
    from app.models.stock import StockMovement
    from app.models.user import User


# ── Site ──────────────────────────────────────────────────


class Site(Base):
    """ORM model for the ``sites`` table.

    Attributes
    ----------
    site_id : int
        Auto-incrementing primary key.
    site_name : str
        Human-readable name of the site.
    location : str | None
        Free-text address / GPS info.
    status : str
        One of the ``SiteStatus`` enum values;
        defaults to ``'active'``.
    created_at : datetime
        UTC timestamp of row creation.
    created_by : int
        FK → ``users.user_id`` of the admin who created
        this site.
    """

    __tablename__ = "sites"

    # ── primary key ───────────────────────────────────────
    site_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # ── core columns ──────────────────────────────────────
    site_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    location: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="active",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_by: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
    )

    # ── relationships ─────────────────────────────────────
    created_by_user: Mapped["User"] = relationship(
        back_populates="created_sites",
    )
    supervisors: Mapped[list["SiteSupervisor"]] = (
        relationship(
            back_populates="site",
            lazy="selectin",
        )
    )
    attendances: Mapped[list["Attendance"]] = relationship(
        back_populates="site",
        lazy="selectin",
    )
    expenses: Mapped[list["Expense"]] = relationship(
        back_populates="site",
        lazy="selectin",
    )
    ajax_logs: Mapped[list["AjaxDriverLog"]] = relationship(
        back_populates="site",
        lazy="selectin",
    )
    hitachi_logs: Mapped[list["HitachiDriverLog"]] = (
        relationship(
            back_populates="site",
            lazy="selectin",
        )
    )
    stock_movements: Mapped[list["StockMovement"]] = (
        relationship(
            back_populates="site",
            lazy="selectin",
        )
    )
    purchases: Mapped[list["Purchase"]] = relationship(
        back_populates="site",
        lazy="selectin",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Site(site_id={self.site_id}, "
            f"site_name={self.site_name!r})>"
        )

