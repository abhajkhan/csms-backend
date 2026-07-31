"""ReportService for reports generation.

Per CSMS_SPEC.md §11.7
"""

from sqlalchemy.ext.asyncio import AsyncSession


class ReportService:
    """Service for reporting operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
