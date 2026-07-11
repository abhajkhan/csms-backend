"""WalletService — placeholder.

Implementation pending Phase 4 — Supervisor Wallet Management.

Critical business rule to implement:
    Every acc_balance update on Users must atomically produce a
    SupervisorBalanceLog entry.
    Per Construction_System_Design_v2.md §8 Supervisor Wallet.
"""

from sqlalchemy.orm import Session


class WalletService:
    """Service for Supervisor Wallet business operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # TODO: Implement wallet credit, debit, and history methods.
