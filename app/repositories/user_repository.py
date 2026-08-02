"""UserRepository for User entity database operations.

Per CSMS_SPEC.md §6.1 & 02_BACKEND_RULES.md §6.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants.enums import UserRole
from app.models.user import User
from app.repositories.base import BaseRepository
from app.utils.pagination import PaginatedResult, PaginationParams, async_paginate


class UserRepository(BaseRepository):
    """Repository for all User database operations."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db)

    async def get_by_id(self, user_id: int) -> User | None:
        """Fetch a User by primary key `user_id`."""
        result = await self.db.execute(
            select(User).where(User.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_phone(self, phone: str) -> User | None:
        """Fetch a User by registered `phone` number."""
        result = await self.db.execute(
            select(User).where(User.phone == phone)
        )
        return result.scalar_one_or_none()

    async def create(self, user: User) -> User:
        """Persist a new `User` instance."""
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def update(self, user: User, update_data: dict) -> User:
        """Update fields on an existing `User` instance."""
        for key, value in update_data.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def deactivate(self, user: User) -> User:
        """Deactivate a user account by setting `is_active = False`."""
        user.is_active = False
        await self.db.flush()
        return user

    async def activate(self, user: User) -> User:
        """Reactivate a user account by setting `is_active = True`."""
        user.is_active = True
        await self.db.flush()
        return user

    async def count_active_admins(self) -> int:
        """Return total count of active Admin accounts."""
        result = await self.db.execute(
            select(func.count()).select_from(User).where(
                User.role == UserRole.ADMIN.value,
                User.is_active.is_(True),
            )
        )
        return result.scalar_one()

    async def list_all(
        self, params: PaginationParams
    ) -> PaginatedResult[User]:
        """List users with pagination."""
        stmt = select(User).order_by(User.user_id)
        return await async_paginate(self.db, stmt, params)
