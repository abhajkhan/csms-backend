"""WalletRepository — placeholder.

Implementation pending Phase 4 — Supervisor Wallet & Worker Payments.
"""

from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository


class WalletRepository(BaseRepository):
    """Repository for SupervisorBalanceLog and WorkerPayment database operations."""

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    # TODO: Implement wallet-specific queries.
