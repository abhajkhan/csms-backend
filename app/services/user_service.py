"""UserService for User management.

Per CSMS_SPEC.md §6.1 & §10.1
"""

from sqlalchemy.ext.asyncio import AsyncSession


class UserService:
    """Service for user administration."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
