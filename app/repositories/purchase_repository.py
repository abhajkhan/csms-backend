"""PurchaseRepository — placeholder.

Implementation pending Phase 5 — Normal Driver Purchase Management.
"""

from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository


class PurchaseRepository(BaseRepository):
    """Repository for all Purchase-related database operations."""

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    # TODO: Implement purchase-specific queries.
