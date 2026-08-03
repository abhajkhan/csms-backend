"""WorkerRepository for Worker entity database operations.

Per CSMS_SPEC.md §6.4 & 02_BACKEND_RULES.md §6.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.worker import Worker
from app.repositories.base import BaseRepository
from app.utils.pagination import PaginatedResult, PaginationParams, async_paginate


class WorkerRepository(BaseRepository):
    """Repository for all Worker database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_by_id(self, worker_id: int) -> Worker | None:
        """Fetch a Worker by primary key `worker_id` (returns both active and inactive workers)."""
        result = await self.db.execute(
            select(Worker).where(Worker.worker_id == worker_id)
        )
        return result.scalar_one_or_none()

    async def create(self, worker: Worker) -> Worker:
        """Persist a new `Worker` instance."""
        self.db.add(worker)
        await self.db.flush()
        await self.db.refresh(worker)
        return worker

    async def update(self, worker: Worker, update_data: dict) -> Worker:
        """Update fields on an existing `Worker` instance."""
        for key, value in update_data.items():
            if hasattr(worker, key) and value is not None:
                setattr(worker, key, value)
        await self.db.flush()
        await self.db.refresh(worker)
        return worker

    async def deactivate(self, worker: Worker) -> Worker:
        """Deactivate a worker account by setting `is_active = False`."""
        worker.is_active = False
        await self.db.flush()
        return worker

    async def activate(self, worker: Worker) -> Worker:
        """Reactivate a worker account by setting `is_active = True`."""
        worker.is_active = True
        await self.db.flush()
        return worker

    async def list_all(
        self, params: PaginationParams, is_active: bool | None = None
    ) -> PaginatedResult[Worker]:
        """List workers with pagination, optionally filtering by `is_active`."""
        stmt = select(Worker)
        if is_active is not None:
            stmt = stmt.where(Worker.is_active.is_(is_active))
        stmt = stmt.order_by(Worker.worker_id)
        return await async_paginate(self.db, stmt, params)
