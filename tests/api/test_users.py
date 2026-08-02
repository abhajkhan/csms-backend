"""User Management API integration tests.

Tests user creation, profile view/edit authorization boundaries, and account deactivation.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User


@pytest.mark.asyncio
async def test_admin_create_user(client: AsyncClient, db_session: AsyncSession) -> None:
    """Admin can create new Admin and Supervisor accounts."""
    admin = User(
        role="admin",
        full_name="Admin Main",
        phone="03006666666",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"phone": "03006666666", "password": "Password123"},
    )
    token = login_res.json()["access_token"]

    create_res = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "full_name": "New Supervisor",
            "phone": "03007777777",
            "password": "SuperPassword123",
            "role": "supervisor",
        },
    )
    assert create_res.status_code == 201
    user_data = create_res.json()
    assert user_data["phone"] == "03007777777"
    assert user_data["role"] == "supervisor"
    assert float(user_data["acc_balance"]) == 0.0

    # Test creating Admin account initializes acc_balance = None
    create_admin_res = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "full_name": "New Sub-Admin",
            "phone": "03007777778",
            "password": "AdminPassword123",
            "role": "admin",
        },
    )
    assert create_admin_res.status_code == 201
    admin_data = create_admin_res.json()
    assert admin_data["role"] == "admin"
    assert admin_data["acc_balance"] is None


@pytest.mark.asyncio
async def test_supervisor_cannot_create_user(client: AsyncClient, db_session: AsyncSession) -> None:
    """Supervisor cannot create user accounts (403 Forbidden)."""
    supervisor = User(
        role="supervisor",
        full_name="Supervisor Only",
        phone="03008888888",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    db_session.add(supervisor)
    await db_session.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"phone": "03008888888", "password": "Password123"},
    )
    token = login_res.json()["access_token"]

    create_res = await client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "full_name": "Unauthorized User",
            "phone": "03009999999",
            "password": "Password123",
            "role": "supervisor",
        },
    )
    assert create_res.status_code == 403


@pytest.mark.asyncio
async def test_supervisor_can_edit_own_profile_only(client: AsyncClient, db_session: AsyncSession) -> None:
    """Supervisor can edit self profile but cannot edit another user profile."""
    sup1 = User(
        role="supervisor",
        full_name="Supervisor One",
        phone="03111111111",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    sup2 = User(
        role="supervisor",
        full_name="Supervisor Two",
        phone="03222222222",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    db_session.add_all([sup1, sup2])
    await db_session.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"phone": "03111111111", "password": "Password123"},
    )
    token = login_res.json()["access_token"]

    # Edit own profile -> 200
    edit_self = await client.patch(
        f"/api/v1/users/{sup1.user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Supervisor One Updated"},
    )
    assert edit_self.status_code == 200
    assert edit_self.json()["full_name"] == "Supervisor One Updated"

    # Edit other profile -> 403
    edit_other = await client.patch(
        f"/api/v1/users/{sup2.user_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Hacked Name"},
    )
    assert edit_other.status_code == 403


@pytest.mark.asyncio
async def test_admin_deactivate_user(client: AsyncClient, db_session: AsyncSession) -> None:
    """Admin can deactivate user (sets is_active = False)."""
    admin = User(
        role="admin",
        full_name="Admin Boss",
        phone="03333333333",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    target = User(
        role="supervisor",
        full_name="Target Sup",
        phone="03444444444",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    db_session.add_all([admin, target])
    await db_session.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"phone": "03333333333", "password": "Password123"},
    )
    token = login_res.json()["access_token"]

    deact_res = await client.delete(
        f"/api/v1/users/{target.user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert deact_res.status_code == 200

    # Verify target cannot login anymore
    target_login = await client.post(
        "/api/v1/auth/login",
        json={"phone": "03444444444", "password": "Password123"},
    )
    assert target_login.status_code == 403

    # Reactivate target user -> 200
    act_res = await client.patch(
        f"/api/v1/users/{target.user_id}/activate",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert act_res.status_code == 200

    # Verify target user can login again -> 200
    target_login_again = await client.post(
        "/api/v1/auth/login",
        json={"phone": "03444444444", "password": "Password123"},
    )
    assert target_login_again.status_code == 200


@pytest.mark.asyncio
async def test_activate_already_active_user_fails(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Activating an already active user returns 422 BusinessRuleException."""
    admin = User(
        role="admin",
        full_name="Admin ActiveTest",
        phone="03777777799",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"phone": "03777777799", "password": "Password123"},
    )
    token = login_res.json()["access_token"]

    act_res = await client.patch(
        f"/api/v1/users/{admin.user_id}/activate",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert act_res.status_code == 422
    assert "User is already active" in act_res.json()["message"]


@pytest.mark.asyncio
async def test_prevent_deactivating_last_active_admin(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Deactivating the last active Admin account fails with 422 BusinessRuleException."""
    # Deactivate pre-existing active admins in test session to isolate single-admin state
    result = await db_session.execute(
        select(User).where(User.role == "admin", User.is_active.is_(True))
    )
    for existing in result.scalars().all():
        existing.is_active = False

    sole_admin = User(
        role="admin",
        full_name="Sole Admin",
        phone="03999999999",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    db_session.add(sole_admin)
    await db_session.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"phone": "03999999999", "password": "Password123"},
    )
    token = login_res.json()["access_token"]

    deact_res = await client.delete(
        f"/api/v1/users/{sole_admin.user_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert deact_res.status_code == 422
    assert "Cannot deactivate the last active Admin account" in deact_res.json()["message"]
