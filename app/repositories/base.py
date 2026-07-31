"""Generic base repository.

Provides async CRUD scaffolding for domain repositories.
Per 02_BACKEND_RULES.md §6 Repository Pattern.
"""

from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    """Abstract base providing common async CRUD scaffolding."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
