"""WalletRepository for SupervisorBalanceLog entity.

Per CSMS_SPEC.md §6.6
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository


class WalletRepository(BaseRepository):
    """Repository for SupervisorBalanceLog database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
