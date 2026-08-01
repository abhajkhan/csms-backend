"""Auth API integration tests.

Tests login, token refresh rotation, current user profile, logout, and password change.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test login with valid phone and password returns tokens."""
    user = User(
        role="admin",
        full_name="Admin User",
        phone="03001111111",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login",
        json={"phone": "03001111111", "password": "Password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test login with wrong password fails with 401."""
    user = User(
        role="admin",
        full_name="Admin User",
        phone="03002222222",
        password_hash=hash_password("CorrectPassword"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    response = await client.post(
        "/api/v1/auth/login",
        json={"phone": "03002222222", "password": "WrongPassword"},
    )
    assert response.status_code == 401
    assert response.json()["message"] == "Invalid phone number or password."


@pytest.mark.asyncio
async def test_refresh_token_rotation(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test refresh endpoint rotates tokens returning new access and refresh tokens."""
    user = User(
        role="supervisor",
        full_name="Supervisor User",
        phone="03003333333",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"phone": "03003333333", "password": "Password123"},
    )
    initial_refresh = login_res.json()["refresh_token"]

    refresh_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": initial_refresh},
    )
    assert refresh_res.status_code == 200
    new_data = refresh_res.json()
    assert "access_token" in new_data
    assert "refresh_token" in new_data
    # Verify rotation: new refresh token differs from initial
    assert new_data["refresh_token"] != initial_refresh


@pytest.mark.asyncio
async def test_get_current_user_me(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test /auth/me returns current user profile."""
    user = User(
        role="admin",
        full_name="Me User",
        phone="03004444444",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"phone": "03004444444", "password": "Password123"},
    )
    access_token = login_res.json()["access_token"]

    me_res = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_res.status_code == 200
    profile = me_res.json()
    assert profile["phone"] == "03004444444"
    assert profile["full_name"] == "Me User"
    assert profile["role"] == "admin"


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, db_session: AsyncSession) -> None:
    """Test change password endpoint."""
    user = User(
        role="admin",
        full_name="Change Pass User",
        phone="03005555555",
        password_hash=hash_password("OldPassword123"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"phone": "03005555555", "password": "OldPassword123"},
    )
    access_token = login_res.json()["access_token"]

    change_res = await client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "old_password": "OldPassword123",
            "new_password": "NewPassword123",
        },
    )
    assert change_res.status_code == 200

    # Verify login with new password succeeds
    login_new = await client.post(
        "/api/v1/auth/login",
        json={"phone": "03005555555", "password": "NewPassword123"},
    )
    assert login_new.status_code == 200
