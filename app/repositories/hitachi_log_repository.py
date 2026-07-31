"""HitachiLogRepository for HitachiDriverLog entity.

Per CSMS_SPEC.md §6.10 & §12
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository


class HitachiLogRepository(BaseRepository):
    """Repository for HitachiDriverLog database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
