"""Authentication Pydantic schemas.

Provides DTOs for auth-related endpoints:
    ``LoginRequest``           — POST /auth/login request body.
    ``RefreshRequest``         — POST /auth/refresh request body.
    ``TokenResponse``          — Token issuance response.
    ``PasswordChangeRequest``  — POST /auth/change-password request body.

Per CSMS_SPEC.md §11.4 & §11.7 and 02_BACKEND_RULES.md §9.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

# ─── Request bodies ───────────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    """Request body for ``POST /auth/login``."""

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
        description="Account password.",
        examples=["secureP@ssw0rd"],
    )

    @field_validator("phone")
    @classmethod
    def _strip_phone(cls, v: str) -> str:
        """Normalise phone number by stripping surrounding whitespace."""
        return v.strip()


class RefreshRequest(BaseModel):
    """Request body for ``POST /auth/refresh``."""

    refresh_token: str = Field(
        ...,
        description="A valid JWT refresh token obtained at login.",
    )


class PasswordChangeRequest(BaseModel):
    """Request body for ``POST /auth/change-password``."""

    old_password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Current account password.",
    )
    new_password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="New account password (min 6 chars).",
    )


# ─── Response bodies ──────────────────────────────────────────────────────────


class TokenResponse(BaseModel):
    """Response body for ``POST /auth/login`` and ``POST /auth/refresh``."""

    access_token: str = Field(
        ...,
        description="Short-lived JWT access token.",
    )
    refresh_token: str = Field(
        ...,
        description="Long-lived JWT refresh token.",
    )
    token_type: str = Field(
        default="bearer",
        description='Token scheme — always "bearer".',
    )
