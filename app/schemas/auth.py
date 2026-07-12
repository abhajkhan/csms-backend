"""Authentication Pydantic schemas.

Provides the request and response DTOs for every auth-related endpoint:
    ``LoginRequest``        — POST /auth/login  request body.
    ``TokenResponse``       — POST /auth/login  and /auth/refresh response.
    ``RefreshRequest``      — POST /auth/refresh request body.
    ``TokenPayloadSchema``  — Internal typed schema mirroring ``TokenPayload``.

Per 03_API_CONTRACT.md §8 Auth Module and
02_BACKEND_RULES.md §8 Authentication.
"""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

# ─── Request bodies ───────────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    """Request body for ``POST /auth/login``.

    Attributes:
        phone:    The user's registered phone number (used as login identifier).
        password: The plain-text password (never stored or logged).
    """

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
    """Request body for ``POST /auth/refresh``.

    Attributes:
        refresh_token: A valid, unexpired JWT refresh token.
    """

    refresh_token: str = Field(
        ...,
        description="A valid JWT refresh token obtained at login.",
    )


# ─── Response bodies ──────────────────────────────────────────────────────────


class TokenResponse(BaseModel):
    """Response body for ``POST /auth/login`` and ``POST /auth/refresh``.

    Both tokens are signed JWTs.  The access token is short-lived (default
    30 min); the refresh token is long-lived (default 7 days).

    Attributes:
        access_token:  JWT for authorising API requests via ``Authorization: Bearer``.
        refresh_token: JWT for obtaining a new access token without re-login.
        token_type:    Always ``"bearer"``.
    """

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
