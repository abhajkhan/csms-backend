"""JWT utilities and password hashing for CSMS backend.

Provides:
    ``hash_password()``         — bcrypt hash a plain-text password.
    ``verify_password()``       — constant-time comparison against a hash.
    ``create_access_token()``   — mint a signed JWT access token.
    ``create_refresh_token()``  — mint a signed JWT refresh token.
    ``decode_token()``          — verify and decode any CSMS JWT.
    ``TokenPayload``            — typed dataclass for decoded token claims.

JWT Payload claims:
    sub         (str)  — ``str(user_id)``; standard JWT subject.
    role        (str)  — ``UserRole`` value embedded at login time.
    driver_type (str | None) — ``DriverType`` value for driver accounts.
    type        (str)  — ``"access"`` or ``"refresh"``.
    exp         (int)  — Unix timestamp of expiry (set by ``python-jose``).
    iat         (int)  — Unix timestamp of issuance.

Per 02_BACKEND_RULES.md §8 Authentication:
    "Never trust client-provided role information.
     Always read permissions from authenticated user."

The role is therefore embedded in the token at login time (read from DB)
and re-read on every request without a database round-trip.

Security notes:
    - Tokens are HS256-signed using ``settings.SECRET_KEY``.
    - Refresh tokens have a longer TTL and carry ``type="refresh"``
      so they cannot be used as access tokens and vice-versa.
    - ``bcrypt`` work factor defaults to passlib's current default (12).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.logging import get_logger
from app.utils.datetime import now_utc

logger = get_logger(__name__)
settings = get_settings()

# ─── Password hashing ─────────────────────────────────────────────────────────


_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

_TOKEN_TYPE_ACCESS = "access"
_TOKEN_TYPE_REFRESH = "refresh"


def hash_password(plain: str) -> str:
    """Return the bcrypt hash of *plain*.

    Args:
        plain: The plain-text password (never stored).

    Returns:
        A bcrypt hash string suitable for storage in the database.
    """
    return _pwd_context.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify *plain* against its bcrypt *hashed* counterpart.

    Uses a constant-time comparison to prevent timing attacks.

    Args:
        plain:  The plain-text password supplied by the user.
        hashed: The hash stored in the database.

    Returns:
        ``True`` when the password matches, ``False`` otherwise.
    """
    return _pwd_context.verify(plain, hashed)


# ─── Token payload ────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class TokenPayload:
    """Decoded and validated JWT claims for a CSMS token.

    Attributes:
        user_id:     The numeric primary key of the authenticated user.
        role:        The ``UserRole`` string embedded at login time.
        driver_type: The ``DriverType`` string for driver accounts, or ``None``.
        token_type:  ``"access"`` or ``"refresh"``.
    """

    user_id: int
    role: str
    driver_type: str | None
    token_type: str


# ─── Token creation ───────────────────────────────────────────────────────────


def _make_token(
    user_id: int,
    role: str,
    driver_type: str | None,
    token_type: str,
    ttl: timedelta,
) -> str:
    """Internal factory — build and sign a JWT with the given claims.

    Args:
        user_id:     The user's numeric primary key.
        role:        The ``UserRole`` value (e.g. ``"admin"``).
        driver_type: The ``DriverType`` value for driver accounts, or ``None``.
        token_type:  ``"access"`` or ``"refresh"``.
        ttl:         Token time-to-live.

    Returns:
        A signed JWT string.
    """
    now = now_utc()
    expire = now + ttl

    payload: dict = {
        "sub": str(user_id),
        "role": role,
        "driver_type": driver_type,
        "type": token_type,
        # Standard claims — python-jose encodes datetimes as Unix timestamps.
        "iat": now,
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def create_access_token(
    user_id: int,
    role: str,
    driver_type: str | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Mint a signed JWT access token.

    Args:
        user_id:      Numeric primary key of the user.
        role:         ``UserRole`` string (e.g. ``"supervisor"``).
        driver_type:  ``DriverType`` string for driver accounts; ``None`` otherwise.
        expires_delta: Custom TTL — defaults to ``ACCESS_TOKEN_EXPIRE_MINUTES``.

    Returns:
        A signed JWT string valid for the configured TTL.
    """
    ttl = expires_delta or timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return _make_token(
        user_id=user_id,
        role=role,
        driver_type=driver_type,
        token_type=_TOKEN_TYPE_ACCESS,
        ttl=ttl,
    )


def create_refresh_token(
    user_id: int,
    role: str,
    driver_type: str | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Mint a signed JWT refresh token.

    Refresh tokens have a longer TTL than access tokens and carry
    ``type="refresh"``, preventing them from being used as access tokens.

    Args:
        user_id:      Numeric primary key of the user.
        role:         ``UserRole`` string.
        driver_type:  ``DriverType`` string for driver accounts; ``None`` otherwise.
        expires_delta: Custom TTL — defaults to ``REFRESH_TOKEN_EXPIRE_DAYS``.

    Returns:
        A signed JWT string valid for the configured TTL.
    """
    ttl = expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _make_token(
        user_id=user_id,
        role=role,
        driver_type=driver_type,
        token_type=_TOKEN_TYPE_REFRESH,
        ttl=ttl,
    )


# ─── Token decoding ───────────────────────────────────────────────────────────


def decode_token(token: str) -> TokenPayload:
    """Verify the JWT signature and decode its claims.

    Raises domain exceptions (never ``HTTPException``) so this function
    can be called safely from services and dependencies alike.

    Args:
        token: A raw JWT string (without the ``Bearer `` prefix).

    Returns:
        A ``TokenPayload`` with the decoded claims.

    Raises:
        ``TokenExpiredException``:  The token's ``exp`` claim is in the past.
        ``InvalidTokenException``:  The signature is invalid, the token is
                                    malformed, or a required claim is missing.
    """
    # Late imports prevent circular dependencies at module load time.
    from jose.exceptions import ExpiredSignatureError

    from app.core.exceptions import InvalidTokenException, TokenExpiredException

    try:
        raw: dict = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except ExpiredSignatureError:
        raise TokenExpiredException()
    except JWTError:
        raise InvalidTokenException()

    # Validate required claims.
    user_id_str: str | None = raw.get("sub")
    role: str | None = raw.get("role")
    token_type: str | None = raw.get("type")

    if not user_id_str or not role or not token_type:
        raise InvalidTokenException()

    try:
        user_id = int(user_id_str)
    except (TypeError, ValueError):
        raise InvalidTokenException()

    return TokenPayload(
        user_id=user_id,
        role=role,
        driver_type=raw.get("driver_type"),
        token_type=token_type,
    )


def decode_access_token(token: str) -> TokenPayload:
    """Decode a token and assert it is an access token.

    Convenience wrapper used by the auth dependency.

    Args:
        token: A raw JWT string.

    Returns:
        A ``TokenPayload`` with ``token_type == "access"``.

    Raises:
        ``InvalidTokenException``: When the token type is not ``"access"``.
        ``TokenExpiredException``: When the token has expired.
    """
    from app.core.exceptions import InvalidTokenException

    payload = decode_token(token)
    if payload.token_type != _TOKEN_TYPE_ACCESS:
        raise InvalidTokenException()
    return payload


def decode_refresh_token(token: str) -> TokenPayload:
    """Decode a token and assert it is a refresh token.

    Used by the ``POST /auth/refresh`` endpoint (Phase 1).

    Args:
        token: A raw JWT string.

    Returns:
        A ``TokenPayload`` with ``token_type == "refresh"``.

    Raises:
        ``InvalidTokenException``: When the token type is not ``"refresh"``.
        ``TokenExpiredException``: When the token has expired.
    """
    from app.core.exceptions import InvalidTokenException

    payload = decode_token(token)
    if payload.token_type != _TOKEN_TYPE_REFRESH:
        raise InvalidTokenException()
    return payload
