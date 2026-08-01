"""AuthService for authentication and password management operations.

Per CSMS_SPEC.md §11.4 & 02_BACKEND_RULES.md §8.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BusinessRuleException,
    InactiveUserException,
    InvalidCredentialsException,
    UserNotFoundException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, PasswordChangeRequest, TokenResponse


class AuthService:
    """Service handling login, token rotation, and password management."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    async def login(self, credentials: LoginRequest) -> TokenResponse:
        """Authenticate user by phone & password and issue JWT tokens."""
        user = await self.user_repo.get_by_phone(credentials.phone)
        if not user or not verify_password(credentials.password, user.password_hash):
            raise InvalidCredentialsException()

        if not user.is_active:
            raise InactiveUserException()

        access_token = create_access_token(
            user_id=user.user_id,
            role=user.role,
            driver_type=user.driver_type,
        )
        refresh_token = create_refresh_token(
            user_id=user.user_id,
            role=user.role,
            driver_type=user.driver_type,
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    async def refresh_tokens(self, refresh_token_str: str) -> TokenResponse:
        """Rotate tokens: validate refresh token & issue new access + refresh pair."""
        payload = decode_refresh_token(refresh_token_str)

        user = await self.user_repo.get_by_id(payload.user_id)
        if not user:
            raise UserNotFoundException(payload.user_id)

        if not user.is_active:
            raise InactiveUserException()

        # Refresh Token Rotation: Mint fresh access token and fresh refresh token
        new_access_token = create_access_token(
            user_id=user.user_id,
            role=user.role,
            driver_type=user.driver_type,
        )
        new_refresh_token = create_refresh_token(
            user_id=user.user_id,
            role=user.role,
            driver_type=user.driver_type,
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer",
        )

    async def change_password(
        self, user_id: int, req: PasswordChangeRequest
    ) -> bool:
        """Change user password after verifying the current password."""
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(user_id)

        if not user.is_active:
            raise InactiveUserException()

        if not verify_password(req.old_password, user.password_hash):
            raise BusinessRuleException("Current password is incorrect.")

        new_hash = hash_password(req.new_password)
        await self.user_repo.update(user, {"password_hash": new_hash})
        await self.db.commit()
        return True
