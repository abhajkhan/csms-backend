"""Authentication API endpoints.

Per CSMS_SPEC.md §11.4 & §11.7 and 02_BACKEND_RULES.md §8.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies.auth import get_current_active_user
from app.schemas.auth import (
    LoginRequest,
    PasswordChangeRequest,
    RefreshRequest,
    TokenResponse,
)
from app.schemas.common import StandardResponse
from app.schemas.user import CurrentUserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user by phone & password and issue access + refresh tokens.",
)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    auth_service = AuthService(db)
    return await auth_service.login(credentials)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Validate refresh token and issue a fresh access token and refresh token pair.",
)
async def refresh_tokens(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    auth_service = AuthService(db)
    return await auth_service.refresh_tokens(body.refresh_token)


@router.post(
    "/logout",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Invalidate session on client side.",
)
async def logout(
    current_user: CurrentUserResponse = Depends(get_current_active_user),
) -> StandardResponse:
    return StandardResponse(
        success=True,
        message="Successfully logged out.",
    )


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Current user profile",
    description="Return authenticated user profile.",
)
async def get_me(
    current_user: CurrentUserResponse = Depends(get_current_active_user),
) -> CurrentUserResponse:
    return current_user


@router.post(
    "/change-password",
    response_model=StandardResponse,
    status_code=status.HTTP_200_OK,
    summary="Change account password",
    description="Change current authenticated user password.",
)
async def change_password(
    req: PasswordChangeRequest,
    current_user: CurrentUserResponse = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> StandardResponse:
    auth_service = AuthService(db)
    await auth_service.change_password(current_user.user_id, req)
    return StandardResponse(
        success=True,
        message="Password changed successfully.",
    )
