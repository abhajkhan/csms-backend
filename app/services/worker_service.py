"""WorkerService for Worker management and domain rules.

Per CSMS_SPEC.md §6.4, §10.1, §10.2 & 02_BACKEND_RULES.md §7.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enums import UserRole
from app.core.exceptions import (
    BusinessRuleException,
    InsufficientRoleException,
    WorkerNotFoundException,
)
from app.models.worker import Worker
from app.repositories.worker_repository import WorkerRepository
from app.schemas.worker import WorkerCreate, WorkerResponse, WorkerUpdate
from app.utils.pagination import PaginationParams


class WorkerService:
    """Service for worker administration and authorization enforcement."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.worker_repo = WorkerRepository(db)

    async def create_worker(
        self, creator_id: int, creator_role: UserRole, worker_in: WorkerCreate
    ) -> Worker:
        """Register a new worker (Admin only)."""
        if creator_role != UserRole.ADMIN:
            raise InsufficientRoleException(["admin"])

        worker = Worker(
            full_name=worker_in.full_name,
            daily_wage=worker_in.daily_wage,
            created_by=creator_id,
            is_active=True,
        )
        created_worker = await self.worker_repo.create(worker)
        await self.db.commit()
        return created_worker

    async def get_worker_by_id(
        self, requester_role: UserRole, worker_id: int
    ) -> Worker:
        """Retrieve a worker profile by ID (Admin or Supervisor). Returns both active and inactive workers."""
        if requester_role not in (UserRole.ADMIN, UserRole.SUPERVISOR):
            raise InsufficientRoleException(["admin", "supervisor"])

        worker = await self.worker_repo.get_by_id(worker_id)
        if not worker:
            raise WorkerNotFoundException(worker_id)
        return worker

    async def update_worker(
        self, requester_role: UserRole, worker_id: int, worker_in: WorkerUpdate
    ) -> Worker:
        """Update worker details (Admin only)."""
        if requester_role != UserRole.ADMIN:
            raise InsufficientRoleException(["admin"])

        worker = await self.worker_repo.get_by_id(worker_id)
        if not worker:
            raise WorkerNotFoundException(worker_id)

        update_dict = worker_in.model_dump(exclude_unset=True)
        updated_worker = await self.worker_repo.update(worker, update_dict)
        await self.db.commit()
        return updated_worker

    async def deactivate_worker(
        self, requester_role: UserRole, worker_id: int
    ) -> Worker:
        """Deactivate a worker (Admin only)."""
        if requester_role != UserRole.ADMIN:
            raise InsufficientRoleException(["admin"])

        worker = await self.worker_repo.get_by_id(worker_id)
        if not worker:
            raise WorkerNotFoundException(worker_id)

        if not worker.is_active:
            raise BusinessRuleException("Worker is already deactivated.")

        deactivated_worker = await self.worker_repo.deactivate(worker)
        await self.db.commit()
        return deactivated_worker

    async def activate_worker(
        self, requester_role: UserRole, worker_id: int
    ) -> Worker:
        """Reactivate a worker (Admin only)."""
        if requester_role != UserRole.ADMIN:
            raise InsufficientRoleException(["admin"])

        worker = await self.worker_repo.get_by_id(worker_id)
        if not worker:
            raise WorkerNotFoundException(worker_id)

        if worker.is_active:
            raise BusinessRuleException("Worker is already active.")

        activated_worker = await self.worker_repo.activate(worker)
        await self.db.commit()
        return activated_worker

    async def list_workers(
        self,
        requester_role: UserRole,
        params: PaginationParams,
        is_active: bool | None = None,
    ) -> dict:
        """List workers with pagination and optional `is_active` filter (Admin or Supervisor)."""
        if requester_role not in (UserRole.ADMIN, UserRole.SUPERVISOR):
            raise InsufficientRoleException(["admin", "supervisor"])

        result = await self.worker_repo.list_all(params, is_active=is_active)
        return {
            "items": [WorkerResponse.model_validate(w) for w in result.items],
            "total": result.total,
            "page": result.page,
            "page_size": result.page_size,
            "total_pages": result.total_pages,
        }
