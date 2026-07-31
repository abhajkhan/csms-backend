"""WorkerPaymentRepository for WorkerPayment entity.

Per CSMS_SPEC.md §6.7 & §12
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository


class WorkerPaymentRepository(BaseRepository):
    """Repository for WorkerPayment database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
