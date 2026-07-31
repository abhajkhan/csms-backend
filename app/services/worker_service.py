"""WorkerService for Worker management.

Per CSMS_SPEC.md §6.4 & §8.5
"""

from sqlalchemy.ext.asyncio import AsyncSession


class WorkerService:
    """Service for worker management."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
