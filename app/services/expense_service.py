"""ExpenseService for site expense management.

Per CSMS_SPEC.md §6.8 & §8.1
"""

from sqlalchemy.ext.asyncio import AsyncSession


class ExpenseService:
    """Service for expense operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
