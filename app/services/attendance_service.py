"""AttendanceService for Attendance domain logic.

Per CSMS_SPEC.md §6.5 & §8.2
"""

from sqlalchemy.ext.asyncio import AsyncSession


class AttendanceService:
    """Service for Attendance business operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
