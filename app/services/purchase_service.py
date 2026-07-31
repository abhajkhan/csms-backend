"""PurchaseService for normal driver purchases.

Per CSMS_SPEC.md §6.15 & §9.5
"""

from sqlalchemy.ext.asyncio import AsyncSession


class PurchaseService:
    """Service for purchase operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
