"""Users API endpoints for user administration.

Per CSMS_SPEC.md §6.1, §10.1 & §11.7 and 02_BACKEND_RULES.md §10.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.dependencies.pagination import get_pagination
from app.dependencies.roles import require_admin
from app.schemas.common import StandardResponse
from app.schemas.user import (
    CurrentUserResponse,
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.services.user_service import UserService
from app.utils.pagination import PaginationParams

router = APIRouter()


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user account",
    description="Create a new Admin or Supervisor account (Admin only).",
)
async def create_user(
    user_in: UserCreate,
    current_user: CurrentUserResponse = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    user_service = UserService(db)
    user = await user_service.create_user(current_user.role, user_in)
    return UserResponse.model_validate(user)


@router.get(
    "",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="List all users",
    description="List all registered user accounts with pagination (Admin only).",
)
async def list_users(
    params: PaginationParams = Depends(get_pagination),
    current_user: CurrentUserResponse = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user_service = UserService(db)
    return await user_service.list_users(current_user.role, params)


@router.get(
    "/{id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user profile",
    description="Get user details by ID (Admin can view any user; Supervisor can view only self).",
)
async def get_user_by_id(
    id: int,
    current_user: CurrentUserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    user_service = UserService(db)
    user = await user_service.get_user_by_id(
        requester_id=current_user.user_id,
        requester_role=current_user.role,
        target_id=id,
    )
    return UserResponse.model_validate(user)


@router.patch(
    "/{id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user details",
    description="Update user profile fields (Admin can update any user; Supervisor can update only self).",
)
async def update_user(
    id: int,
    user_in: UserUpdate,
    current_user: CurrentUserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    user_service = UserService(db)
    user = await user_service.update_user(
        requester_id=current_user.user_id,
        requester_role=current_user.role,
        target_id=id,
        user_in=user_in,
    )
    return UserResponse.model_validate(user)


@router.delete(
    "/{id}",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Deactivate user",
    description="Deactivate a user account by setting is_active = False (Admin only).",
)
async def deactivate_user(
    id: int,
    current_user: CurrentUserResponse = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse:
    user_service = UserService(db)
    await user_service.deactivate_user(
        requester_role=current_user.role,
        target_id=id,
    )
    return StandardResponse(
        success=True,
        message=f"User id={id} was successfully deactivated.",
    )
