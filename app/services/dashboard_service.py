"""DashboardService for executive dashboard analytics.

Per CSMS_SPEC.md §11.7
"""

from sqlalchemy.ext.asyncio import AsyncSession


class DashboardService:
    """Service for dashboard metrics operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
