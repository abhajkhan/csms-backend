"""ExpenseService — placeholder.

Implementation pending Phase 4 — Expense Management.

Critical business rule to implement:
    Every expense creation must atomically debit the supervisor wallet
    and produce a SupervisorBalanceLog entry.
    Per Construction_System_Design_v2.md §8 Transaction Integrity.
"""

from sqlalchemy.orm import Session


class ExpenseService:
    """Service for Expense business operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # TODO: Implement expense service methods.
