"""SiteSupervisor ORM model.

Table: ``site_supervisors``
Design reference: CSMS_SPEC.md §6.3

Junction table for many-to-many assignment between supervisors and sites.
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
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.site import Site
    from app.models.user import User


class SiteSupervisor(Base):
    """ORM model for the ``site_supervisors`` table.

    Junction / association table linking supervisors to the
    sites they are assigned to.
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
    site: Mapped[Site] = relationship(
        "Site",
        back_populates="supervisors",
    )
    supervisor: Mapped[User] = relationship(
        "User",
        back_populates="site_assignments",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<SiteSupervisor(id={self.id}, "
            f"site_id={self.site_id}, "
            f"supervisor_id={self.supervisor_id})>"
        )
