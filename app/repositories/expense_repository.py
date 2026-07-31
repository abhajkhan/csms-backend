"""ExpenseRepository for Expense entity.

Per CSMS_SPEC.md §6.8
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository


class ExpenseRepository(BaseRepository):
    """Repository for Expense database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
