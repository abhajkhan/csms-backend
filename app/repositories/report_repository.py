"""ReportRepository for aggregation and analytics queries.

Per CSMS_SPEC.md §11.7
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository


class ReportRepository(BaseRepository):
    """Repository for reporting query operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
