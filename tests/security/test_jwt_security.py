"""JWT Security tests.

Tests invalid/expired/tampered tokens, refresh token misuses, inactive users, and RBAC boundary enforcement.
"""

from datetime import timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, hash_password
from app.models.user import User


@pytest.mark.asyncio
async def test_invalid_jwt_signature(client: AsyncClient) -> None:
    """Tampered or invalid signature token must return 401."""
    invalid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalidpayload.invalidsignature"
    res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    assert res.status_code == 401
    assert res.json()["message"] == "Authentication token is invalid."


@pytest.mark.asyncio
async def test_expired_jwt_token(client: AsyncClient, db_session: AsyncSession) -> None:
    """Expired access token must return 401."""
    user = User(
        role="admin",
        full_name="Expired User",
        phone="03555555555",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    expired_token = create_access_token(
        user_id=user.user_id,
        role="admin",
        expires_delta=timedelta(seconds=-10),
    )

    res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert res.status_code == 401
    assert res.json()["message"] == "Authentication token has expired."


@pytest.mark.asyncio
async def test_refresh_token_used_as_access_token(client: AsyncClient, db_session: AsyncSession) -> None:
    """Passing a refresh token in the Authorization header must fail with 401."""
    user = User(
        role="admin",
        full_name="Token Swap User",
        phone="03666666666",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    refresh_token = create_refresh_token(user_id=user.user_id, role="admin")

    res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )
    assert res.status_code == 401
    assert res.json()["message"] == "Authentication token is invalid."


@pytest.mark.asyncio
async def test_deactivated_user_token_access_denied(client: AsyncClient, db_session: AsyncSession) -> None:
    """Authenticated request with token belonging to a deactivated user must return 403."""
    user = User(
        role="supervisor",
        full_name="Deactivated User",
        phone="03777777777",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    token = create_access_token(user_id=user.user_id, role="supervisor")

    # Deactivate user in database
    user.is_active = False
    await db_session.commit()

    res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 403
    assert "deactivated" in res.json()["message"].lower()


@pytest.mark.asyncio
async def test_supervisor_role_guard_restriction(client: AsyncClient, db_session: AsyncSession) -> None:
    """Supervisor accessing admin-only endpoint /users must return 403."""
    supervisor = User(
        role="supervisor",
        full_name="Supervisor User Guard",
        phone="03888888888",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    db_session.add(supervisor)
    await db_session.commit()

    token = create_access_token(user_id=supervisor.user_id, role="supervisor")

    res = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert res.status_code == 403
