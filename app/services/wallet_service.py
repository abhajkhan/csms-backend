"""WalletService for supervisor wallet management.

Per CSMS_SPEC.md §6.6 & §8.1
"""

from sqlalchemy.ext.asyncio import AsyncSession


class WalletService:
    """Service for supervisor wallet operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
