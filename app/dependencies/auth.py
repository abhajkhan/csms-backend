"""Authentication FastAPI dependencies.

Provides:
    ``oauth2_scheme``             — Bearer token extractor.
    ``get_current_user``          — Decodes the JWT and fetches the user from DB.
    ``get_current_active_user``   — Asserts the user account is active.

These dependencies form the foundation of every protected endpoint.
Route handlers use them via ``Depends()``::

    @router.get("/workers")
    def list_workers(
        current_user: CurrentUserResponse = Depends(get_current_active_user),
        db: Session = Depends(get_db),
    ):
        ...

Dependency chain:
    OAuth2PasswordBearer  →  get_current_user  →  get_current_active_user
                                   ↓
                      decode_access_token (JWT verify)
                                   ↓
                     DB lookup: user must exist (Phase 1)
                                   ↓
                     InactiveUserException if is_active=False

Phase 0.3 scope:
    - JWT decoding and claim validation are fully implemented.
    - Database lookup of the user record is **stubbed** and will be wired
      to ``UserRepository`` in Phase 1 when the User model exists.
    - Until Phase 1, ``get_current_user`` returns a ``CurrentUserResponse``
      built directly from the JWT payload (no DB round-trip).

Per 02_BACKEND_RULES.md §8 Authentication.
"""

from __future__ import annotations

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.exceptions import (
    AuthenticationException,
    InactiveUserException,
)
from app.core.security import decode_access_token
from app.schemas.user import CurrentUserResponse

# OAuth2 Bearer scheme — extracts the token from ``Authorization: Bearer <token>``.
# ``tokenUrl`` must point to the login endpoint (used by Swagger UI only).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
) -> CurrentUserResponse:
    """Decode the Bearer token and return the authenticated user.

    This dependency runs on every protected request:
        1. Extracts the ``Authorization: Bearer <token>`` header.
        2. Decodes and verifies the JWT signature and expiry.
        3. Fetches the User record from the database (Phase 1).
        4. Returns a ``CurrentUserResponse`` DTO.

    Args:
        token: Raw JWT string extracted by ``OAuth2PasswordBearer``.
               ``None`` when no ``Authorization`` header is present.

    Returns:
        ``CurrentUserResponse`` populated from the decoded JWT claims.

    Raises:
        ``AuthenticationException`` (401): When no token is provided.
        ``TokenExpiredException``  (401): When the token has expired.
        ``InvalidTokenException``  (401): When the token is malformed.
        ``InactiveUserException``  (403): When the user account is deactivated
                                          (enforced in Phase 1).
    """
    if token is None:
        raise AuthenticationException(
            "Authentication credentials were not provided."
        )

    # Decode and validate the access token (raises TokenExpiredException /
    # InvalidTokenException on failure).
    payload = decode_access_token(token)

    # ── Phase 1: replace this block with a real UserRepository lookup ────────
    # When the User ORM model is available, the dependency should:
    #   1. Call UserRepository.get_by_id(db, payload.user_id)
    #   2. Raise UserNotFoundException if the user does not exist.
    #   3. Raise InactiveUserException if user.is_active is False.
    #   4. Return CurrentUserResponse.model_validate(user)
    #
    # For now, we build the response purely from JWT claims.
    # ─────────────────────────────────────────────────────────────────────────

    return CurrentUserResponse(
        user_id=payload.user_id,
        role=payload.role,  # type: ignore[arg-type]
        driver_type=payload.driver_type,  # type: ignore[arg-type]
        full_name="",   # Populated from DB in Phase 1
        phone="",       # Populated from DB in Phase 1
        is_active=True,
    )


async def get_current_active_user(
    current_user: CurrentUserResponse = Depends(get_current_user),
) -> CurrentUserResponse:
    """Assert the authenticated user account is active.

    Wraps ``get_current_user`` and raises ``InactiveUserException`` (403)
    when the user account has been deactivated.

    All protected endpoints that require an active account should depend on
    this function rather than ``get_current_user`` directly.

    Args:
        current_user: The authenticated user returned by ``get_current_user``.

    Returns:
        The same ``CurrentUserResponse`` when the account is active.

    Raises:
        ``InactiveUserException`` (403): When ``current_user.is_active`` is ``False``.
    """
    if not current_user.is_active:
        raise InactiveUserException()
    return current_user
