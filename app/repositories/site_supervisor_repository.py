"""SiteSupervisorRepository for SiteSupervisor entity.

Per CSMS_SPEC.md §6.3 & §12
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository


class SiteSupervisorRepository(BaseRepository):
    """Repository for SiteSupervisor database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
