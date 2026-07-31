"""SiteSupervisorService for site supervisor assignments.

Per CSMS_SPEC.md §6.3 & §12
"""

from sqlalchemy.ext.asyncio import AsyncSession


class SiteSupervisorService:
    """Service for managing site-supervisor assignments."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
