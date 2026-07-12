"""User Pydantic schemas.

Provides the DTOs for user-related API responses.

This module intentionally defines **only** the schemas required by the auth
dependency layer (Phase 0.3).  Full user management schemas
(``UserCreate``, ``UserUpdate``, paginated lists, etc.) will be added in
Phase 1 — Auth & User Management.

Per 03_API_CONTRACT.md §8 Users Module and
02_BACKEND_RULES.md §12 Response Format.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from app.constants.enums import DriverType, UserRole

# ─── Auth-layer schemas (Phase 0.3) ──────────────────────────────────────────


class CurrentUserResponse(BaseModel):
    """Profile of the authenticated user returned by ``GET /auth/me``.

    Populated by ``get_current_user`` from the decoded JWT payload and
    (in Phase 1) a database lookup to verify ``is_active``.

    Attributes:
        user_id:     Numeric primary key.
        role:        Top-level role (admin / supervisor / driver).
        driver_type: Sub-type for driver accounts; ``None`` for others.
        full_name:   Display name of the user.
        phone:       Registered phone number (login identifier).
        is_active:   ``False`` when the account has been deactivated.
    """

    user_id: int = Field(..., description="User primary key.")
    role: UserRole = Field(..., description="Top-level user role.")
    driver_type: DriverType | None = Field(
        default=None,
        description="Driver sub-type; null for non-driver accounts.",
    )
    full_name: str = Field(..., description="User display name.")
    phone: str = Field(..., description="Registered phone number.")
    is_active: bool = Field(default=True, description="Account active status.")

    model_config = {"from_attributes": True}


# ─── Full management schemas (Phase 1 — placeholder) ─────────────────────────

# UserCreate, UserUpdate, UserListResponse — to be implemented in Phase 1.
