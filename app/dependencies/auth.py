"""Authentication FastAPI dependencies.

Provides:
    ``oauth2_scheme``             — Bearer token extractor.
    ``get_current_user``          — Decodes the JWT and fetches the user from DB.
    ``get_current_active_user``   — Asserts the user account is active.

Per 02_BACKEND_RULES.md §9 & CSMS_SPEC.md §11.4.
"""

from __future__ import annotations

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AuthenticationException,
    InactiveUserException,
    UserNotFoundException,
)
from app.core.security import decode_access_token
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.user import CurrentUserResponse

# OAuth2 Bearer scheme — extracts token from ``Authorization: Bearer <token>``.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> CurrentUserResponse:
    """Decode the Bearer token and return the authenticated user from the database."""
    if token is None:
        raise AuthenticationException(
            "Authentication credentials were not provided."
        )

    payload = decode_access_token(token)

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(payload.user_id)

    if not user:
        raise UserNotFoundException(payload.user_id)

    if not user.is_active:
        raise InactiveUserException()

    return CurrentUserResponse.model_validate(user)


async def get_current_active_user(
    current_user: CurrentUserResponse = Depends(get_current_user),
) -> CurrentUserResponse:
    """Assert the authenticated user account is active."""
    if not current_user.is_active:
        raise InactiveUserException()
    return current_user
