"""User Pydantic schemas.

Provides DTOs for user creation, update, and response representation.

Per CSMS_SPEC.md §6.1, §10.1 & §11.7 and 02_BACKEND_RULES.md §12.
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.constants.enums import DriverType, UserRole


class CurrentUserResponse(BaseModel):
    """Profile of the authenticated user returned by ``GET /auth/me``."""

    user_id: int = Field(..., description="User primary key.")
    role: UserRole = Field(..., description="Top-level user role.")
    driver_type: DriverType | None = Field(
        default=None,
        description="Driver sub-type; null for non-driver accounts.",
    )
    full_name: str = Field(..., description="User display name.")
    phone: str = Field(..., description="Registered phone number.")
    is_active: bool = Field(default=True, description="Account active status.")
    acc_balance: Decimal | None = Field(
        default=None, 
        examples=[1000.00],
        description="Current wallet/account balance."
    )

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """Request body for creating a user account (Admin only)."""

    full_name: str = Field(
        ...,
        min_length=2,
        max_length=255,
        description="Full name of the user.",
        examples=["John Doe"],
    )
    phone: str = Field(
        ...,
        min_length=7,
        max_length=20,
        description="Registered phone number.",
        examples=["03001234567"],
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Account password (min 6 chars).",
        examples=["secureP@ssw0rd"],
    )
    role: UserRole = Field(
        ...,
        description="User role (must be 'admin' or 'supervisor').",
    )
    acc_balance: Decimal | None = Field(
        default=None,
        description="Initial account balance for supervisor wallet if applicable.",
    )

    @field_validator("phone")
    @classmethod
    def _strip_phone(cls, v: str) -> str:
        return v.strip()

    @field_validator("role")
    @classmethod
    def _validate_role(cls, v: UserRole) -> UserRole:
        if v not in (UserRole.ADMIN, UserRole.SUPERVISOR):
            raise ValueError("Only 'admin' and 'supervisor' accounts can be created.")
        return v


class UserUpdate(BaseModel):
    """Request body for updating a user profile.

    Note: Password changes are strictly prohibited here and must use
    ``POST /auth/change-password``.
    """

    full_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=255,
        description="Updated full name.",
    )
    phone: str | None = Field(
        default=None,
        min_length=7,
        max_length=20,
        description="Updated phone number.",
    )

    @field_validator("phone")
    @classmethod
    def _strip_phone(cls, v: str | None) -> str | None:
        return v.strip() if v is not None else None


class UserResponse(BaseModel):
    """Response DTO for user profile representations."""

    user_id: int = Field(..., description="User primary key.")
    role: UserRole = Field(..., description="User role.")
    driver_type: DriverType | None = Field(
        default=None, description="Driver sub-type if applicable."
    )
    full_name: str = Field(..., description="User full name.")
    phone: str = Field(..., description="User phone number.")
    is_active: bool = Field(..., description="Active status.")
    acc_balance: Decimal | None = Field(
        default=None,
        examples=[1000.00],
        description="Current wallet/account balance."
    )

    model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
    """Paginated response DTO for user listings."""

    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
