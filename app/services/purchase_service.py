"""PurchaseService — placeholder.

Implementation pending Phase 5 — Normal Driver Purchase Management.
"""

from sqlalchemy.orm import Session


class PurchaseService:
    """Service for Purchase business operations (normal driver only)."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # TODO: Implement purchase service methods.
