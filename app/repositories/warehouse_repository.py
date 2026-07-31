"""WarehouseRepository for Warehouse, WarehouseItem, WarehouseStock entities.

Per CSMS_SPEC.md §6.11, §6.12, §6.13
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.base import BaseRepository


class WarehouseRepository(BaseRepository):
    """Repository for Warehouse database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)
