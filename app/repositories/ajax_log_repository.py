"""AjaxLogRepository for AjaxDriverLog entity.

Per CSMS_SPEC.md §6.9 & §12
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository


class AjaxLogRepository(BaseRepository):
    """Repository for AjaxDriverLog database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
