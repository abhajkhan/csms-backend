"""UserService for User management and domain rules.

Per CSMS_SPEC.md §6.1, §10.1 & 02_BACKEND_RULES.md §7.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enums import UserRole
from app.core.exceptions import (
    AuthorizationException,
    BusinessRuleException,
    InsufficientRoleException,
    PhoneAlreadyRegisteredException,
    UserNotFoundException,
)
from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.utils.pagination import PaginationParams


class UserService:
    """Service for user administration and authorization enforcement."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.user_repo = UserRepository(db)

    async def create_user(
        self, creator_role: UserRole, user_in: UserCreate
    ) -> User:
        """Register a new user account (Admin only)."""
        if creator_role != UserRole.ADMIN:
            raise InsufficientRoleException(["admin"])

        if user_in.role not in (UserRole.ADMIN, UserRole.SUPERVISOR):
            raise BusinessRuleException(
                "Only Admin and Supervisor user accounts can be created."
            )

        existing = await self.user_repo.get_by_phone(user_in.phone)
        if existing:
            raise PhoneAlreadyRegisteredException(user_in.phone)

        password_hash = hash_password(user_in.password)
        user = User(
            role=user_in.role.value,
            full_name=user_in.full_name,
            phone=user_in.phone,
            password_hash=password_hash,
            acc_balance=user_in.acc_balance,
            is_active=True,
        )
        created_user = await self.user_repo.create(user)
        await self.db.commit()
        return created_user

    async def get_user_by_id(
        self, requester_id: int, requester_role: UserRole, target_id: int
    ) -> User:
        """Retrieve a user profile by ID with role-based access check."""
        if requester_role != UserRole.ADMIN and requester_id != target_id:
            raise AuthorizationException(
                "You are only allowed to view your own profile."
            )

        user = await self.user_repo.get_by_id(target_id)
        if not user:
            raise UserNotFoundException(target_id)
        return user

    async def update_user(
        self,
        requester_id: int,
        requester_role: UserRole,
        target_id: int,
        user_in: UserUpdate,
    ) -> User:
        """Update a user profile with role-based access check."""
        if requester_role != UserRole.ADMIN and requester_id != target_id:
            raise AuthorizationException(
                "You are only allowed to update your own profile."
            )

        user = await self.user_repo.get_by_id(target_id)
        if not user:
            raise UserNotFoundException(target_id)

        update_dict = user_in.model_dump(exclude_unset=True)

        if "phone" in update_dict and update_dict["phone"] != user.phone:
            existing = await self.user_repo.get_by_phone(update_dict["phone"])
            if existing and existing.user_id != target_id:
                raise PhoneAlreadyRegisteredException(update_dict["phone"])

        updated_user = await self.user_repo.update(user, update_dict)
        await self.db.commit()
        return updated_user

    async def deactivate_user(
        self, requester_role: UserRole, target_id: int
    ) -> User:
        """Deactivate a user account (Admin only)."""
        if requester_role != UserRole.ADMIN:
            raise InsufficientRoleException(["admin"])

        user = await self.user_repo.get_by_id(target_id)
        if not user:
            raise UserNotFoundException(target_id)

        deactivated_user = await self.user_repo.deactivate(user)
        await self.db.commit()
        return deactivated_user

    async def list_users(
        self, requester_role: UserRole, params: PaginationParams
    ) -> dict:
        """List all users with pagination (Admin only)."""
        if requester_role != UserRole.ADMIN:
            raise InsufficientRoleException(["admin"])

        result = await self.user_repo.list_all(params)
        return {
            "items": [UserResponse.model_validate(u) for u in result.items],
            "total": result.total,
            "page": result.page,
            "page_size": result.page_size,
            "total_pages": result.total_pages,
        }
