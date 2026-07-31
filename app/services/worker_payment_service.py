"""WorkerPaymentService for worker advances and payments.

Per CSMS_SPEC.md §6.7 & §12
"""

from sqlalchemy.ext.asyncio import AsyncSession


class WorkerPaymentService:
    """Service for worker payments operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
