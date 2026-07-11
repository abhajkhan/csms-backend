"""UserRepository — placeholder.

Implementation pending Phase 1 — Auth & User Management.
"""

from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    """Repository for all User-related database operations."""

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    # TODO: Implement user-specific queries.
