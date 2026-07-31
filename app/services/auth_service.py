"""AuthService for authentication logic.

Per CSMS_SPEC.md §11.4
"""

from sqlalchemy.ext.asyncio import AsyncSession


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
