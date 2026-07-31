"""UserRepository for User entity.

Per CSMS_SPEC.md §6.1
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    """Repository for all User-related database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
