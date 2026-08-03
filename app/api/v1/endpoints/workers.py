"""Workers endpoints for worker administration and listing.

Per CSMS_SPEC.md §6.4, §10.1, §10.2 & §11.7 and 02_BACKEND_RULES.md §10 & §19.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.dependencies.pagination import get_pagination
from app.dependencies.roles import require_admin
from app.schemas.common import StandardResponse
from app.schemas.user import CurrentUserResponse
from app.schemas.worker import (
    WorkerCreate,
    WorkerListResponse,
    WorkerResponse,
    WorkerUpdate,
)
from app.services.worker_service import WorkerService
from app.utils.pagination import PaginationParams

router = APIRouter()


@router.post(
    "",
    response_model=WorkerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register worker",
    description="Register a new worker with full name and daily wage (Admin only).",
)
async def create_worker(
    worker_in: WorkerCreate,
    current_user: CurrentUserResponse = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> WorkerResponse:
    worker_service = WorkerService(db)
    worker = await worker_service.create_worker(
        creator_id=current_user.user_id,
        creator_role=current_user.role,
        worker_in=worker_in,
    )
    return WorkerResponse.model_validate(worker)


@router.get(
    "",
    response_model=WorkerListResponse,
    status_code=status.HTTP_200_OK,
    summary="List workers",
    description=(
        "List all worker accounts with pagination (Admin and Supervisor). "
        "Filter by active status using ?is_active=true or ?is_active=false. "
        "When omitted, returns all workers."
    ),
)
async def list_workers(
    is_active: bool | None = Query(
        default=None,
        description="Filter workers by active status. When omitted, returns all workers.",
    ),
    params: PaginationParams = Depends(get_pagination),
    current_user: CurrentUserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> WorkerListResponse:
    worker_service = WorkerService(db)
    result = await worker_service.list_workers(
        requester_role=current_user.role,
        params=params,
        is_active=is_active,
    )
    return WorkerListResponse(**result)


@router.get(
    "/{id}",
    response_model=WorkerResponse,
    status_code=status.HTTP_200_OK,
    summary="Get worker profile",
    description="Get worker details by ID (Admin and Supervisor). Returns active and inactive workers.",
)
async def get_worker_by_id(
    id: int,
    current_user: CurrentUserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> WorkerResponse:
    worker_service = WorkerService(db)
    worker = await worker_service.get_worker_by_id(
        requester_role=current_user.role,
        worker_id=id,
    )
    return WorkerResponse.model_validate(worker)


@router.patch(
    "/{id}",
    response_model=WorkerResponse,
    status_code=status.HTTP_200_OK,
    summary="Update worker details",
    description="Update worker full name or daily wage rate (Admin only).",
)
async def update_worker(
    id: int,
    worker_in: WorkerUpdate,
    current_user: CurrentUserResponse = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> WorkerResponse:
    worker_service = WorkerService(db)
    worker = await worker_service.update_worker(
        requester_role=current_user.role,
        worker_id=id,
        worker_in=worker_in,
    )
    return WorkerResponse.model_validate(worker)


@router.patch(
    "/{id}/activate",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Reactivate worker",
    description="Reactivate a worker account by setting is_active = True (Admin only).",
)
async def activate_worker(
    id: int,
    current_user: CurrentUserResponse = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse:
    worker_service = WorkerService(db)
    await worker_service.activate_worker(
        requester_role=current_user.role,
        worker_id=id,
    )
    return StandardResponse(
        success=True,
        message=f"Worker id={id} was successfully activated.",
    )


@router.delete(
    "/{id}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Deactivate worker",
    description="Deactivate a worker account by setting is_active = False (Admin only).",
)
async def deactivate_worker(
    id: int,
    current_user: CurrentUserResponse = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse:
    worker_service = WorkerService(db)
    await worker_service.deactivate_worker(
        requester_role=current_user.role,
        worker_id=id,
    )
    return StandardResponse(
        success=True,
        message=f"Worker id={id} was successfully deactivated.",
    )
