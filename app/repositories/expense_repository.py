"""ExpenseRepository — placeholder.

Implementation pending Phase 4 — Expense Management.
"""

from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository


class ExpenseRepository(BaseRepository):
    """Repository for all Expense-related database operations."""

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    # TODO: Implement expense-specific queries.
