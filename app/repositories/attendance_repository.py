"""AttendanceRepository for Attendance entity.

Per CSMS_SPEC.md §6.5
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository


class AttendanceRepository(BaseRepository):
    """Repository for Attendance database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
