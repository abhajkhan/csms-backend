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
    from app.models.attendance import Attendance
    from app.models.expense import Expense
    from app.models.purchase import Purchase
    from app.models.stock import AjaxDriverLog, HitachiDriverLog, StockMovement
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


# ── SiteSupervisor ────────────────────────────────────────


class SiteSupervisor(Base):
    """ORM model for the ``site_supervisors`` table.

    Junction / association table linking supervisors to the
    sites they are assigned to.

    Attributes
    ----------
    id : int
        Auto-incrementing surrogate primary key.
    site_id : int
        FK → ``sites.site_id``.
    supervisor_id : int
        FK → ``users.user_id``.
    assigned_at : datetime
        UTC timestamp of when the assignment was made.
    is_active : bool
        Soft-delete flag for the assignment.
    """

    __tablename__ = "site_supervisors"
    __table_args__ = (
        UniqueConstraint(
            "site_id",
            "supervisor_id",
            name="uq_site_supervisor",
        ),
        Index(
            "ix_site_supervisor_active",
            "site_id",
            "supervisor_id",
            "is_active",
        ),
    )

    # ── primary key ───────────────────────────────────────
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # ── foreign keys ──────────────────────────────────────
    site_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("sites.site_id"),
        nullable=False,
    )
    supervisor_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.user_id"),
        nullable=False,
    )

    # ── timestamps / flags ────────────────────────────────
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # ── relationships ─────────────────────────────────────
    site: Mapped["Site"] = relationship(
        back_populates="supervisors",
    )
    supervisor: Mapped["User"] = relationship(
        back_populates="site_assignments",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<SiteSupervisor(id={self.id}, "
            f"site_id={self.site_id}, "
            f"supervisor_id={self.supervisor_id})>"
        )
