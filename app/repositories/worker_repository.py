"""WorkerRepository for Worker entity.

Per CSMS_SPEC.md §6.4
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository


class WorkerRepository(BaseRepository):
    """Repository for Worker database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
