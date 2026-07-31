"""StockRepository for StockMovement entity.

Per CSMS_SPEC.md §6.14
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository


class StockRepository(BaseRepository):
    """Repository for StockMovement database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
