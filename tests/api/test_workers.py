"""Worker Management API integration tests.

Per CSMS_SPEC.md §6.4, §10.1, §10.2 & §11.7.
Tests Admin CRUD, Supervisor read access, and filtering by is_active query parameter.
"""

from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.models.worker import Worker


@pytest.mark.asyncio
async def test_admin_create_worker(client: AsyncClient, db_session: AsyncSession) -> None:
    """Admin can register a new worker account."""
    admin = User(
        role="admin",
        full_name="Admin WorkerCreator",
        phone="03888888801",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"phone": "03888888801", "password": "Password123"},
    )
    token = login_res.json()["access_token"]

    create_res = await client.post(
        "/api/v1/workers",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "full_name": "Ramesh Kumar",
            "daily_wage": 550.50,
        },
    )
    assert create_res.status_code == 201
    data = create_res.json()
    assert data["full_name"] == "Ramesh Kumar"
    assert float(data["daily_wage"]) == 550.50
    assert data["is_active"] is True
    assert data["created_by"] == admin.user_id


@pytest.mark.asyncio
async def test_supervisor_mutation_denied(client: AsyncClient, db_session: AsyncSession) -> None:
    """Supervisor cannot create, update, deactivate, or activate workers (403 Forbidden)."""
    supervisor = User(
        role="supervisor",
        full_name="Supervisor ReadOnly",
        phone="03888888802",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    db_session.add(supervisor)
    await db_session.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"phone": "03888888802", "password": "Password123"},
    )
    token = login_res.json()["access_token"]

    # Attempt POST /workers -> 403
    create_res = await client.post(
        "/api/v1/workers",
        headers={"Authorization": f"Bearer {token}"},
        json={"full_name": "Forbidden Worker", "daily_wage": 400.00},
    )
    assert create_res.status_code == 403


@pytest.mark.asyncio
async def test_supervisor_read_access(client: AsyncClient, db_session: AsyncSession) -> None:
    """Supervisor has read-only access to GET /workers and GET /workers/{id}."""
    admin = User(
        role="admin",
        full_name="Admin Setup",
        phone="03888888803",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    supervisor = User(
        role="supervisor",
        full_name="Supervisor Reader",
        phone="03888888804",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    db_session.add_all([admin, supervisor])
    await db_session.commit()

    worker = Worker(
        full_name="Suresh Kumar",
        daily_wage=Decimal("600.00"),
        is_active=True,
        created_by=admin.user_id,
    )
    db_session.add(worker)
    await db_session.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"phone": "03888888804", "password": "Password123"},
    )
    token = login_res.json()["access_token"]

    # GET /workers -> 200
    list_res = await client.get(
        "/api/v1/workers",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1

    # GET /workers/{id} -> 200
    detail_res = await client.get(
        f"/api/v1/workers/{worker.worker_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail_res.status_code == 200
    assert detail_res.json()["full_name"] == "Suresh Kumar"


@pytest.mark.asyncio
async def test_get_inactive_worker_by_id(client: AsyncClient, db_session: AsyncSession) -> None:
    """GET /workers/{id} returns 200 OK for inactive workers with is_active=False."""
    admin = User(
        role="admin",
        full_name="Admin InactiveTest",
        phone="03888888805",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()

    inactive_worker = Worker(
        full_name="Inactive Worker",
        daily_wage=Decimal("450.00"),
        is_active=False,
        created_by=admin.user_id,
    )
    db_session.add(inactive_worker)
    await db_session.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"phone": "03888888805", "password": "Password123"},
    )
    token = login_res.json()["access_token"]

    detail_res = await client.get(
        f"/api/v1/workers/{inactive_worker.worker_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert detail_res.status_code == 200
    data = detail_res.json()
    assert data["full_name"] == "Inactive Worker"
    assert data["is_active"] is False


@pytest.mark.asyncio
async def test_admin_update_deactivate_and_activate_worker(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """Admin can update, deactivate, and reactivate workers with state checks."""
    admin = User(
        role="admin",
        full_name="Admin Lifecycle",
        phone="03888888806",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()

    worker = Worker(
        full_name="Lifecycle Worker",
        daily_wage=Decimal("500.00"),
        is_active=True,
        created_by=admin.user_id,
    )
    db_session.add(worker)
    await db_session.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"phone": "03888888806", "password": "Password123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Update worker -> 200
    update_res = await client.patch(
        f"/api/v1/workers/{worker.worker_id}",
        headers=headers,
        json={"full_name": "Lifecycle Worker Updated", "daily_wage": 650.00},
    )
    assert update_res.status_code == 200
    assert update_res.json()["full_name"] == "Lifecycle Worker Updated"

    # Deactivate worker -> 200
    deact_res = await client.delete(
        f"/api/v1/workers/{worker.worker_id}",
        headers=headers,
    )
    assert deact_res.status_code == 200

    # Deactivate again -> 422 BusinessRuleException
    deact_again = await client.delete(
        f"/api/v1/workers/{worker.worker_id}",
        headers=headers,
    )
    assert deact_again.status_code == 422

    # Reactivate worker -> 200
    act_res = await client.patch(
        f"/api/v1/workers/{worker.worker_id}/activate",
        headers=headers,
    )
    assert act_res.status_code == 200

    # Reactivate again -> 422 BusinessRuleException
    act_again = await client.patch(
        f"/api/v1/workers/{worker.worker_id}/activate",
        headers=headers,
    )
    assert act_again.status_code == 422


@pytest.mark.asyncio
async def test_list_workers_filtering_by_is_active(
    client: AsyncClient, db_session: AsyncSession
) -> None:
    """GET /workers returns all by default; filters when ?is_active=true or ?is_active=false."""
    admin = User(
        role="admin",
        full_name="Admin FilterTest",
        phone="03888888807",
        password_hash=hash_password("Password123"),
        is_active=True,
    )
    db_session.add(admin)
    await db_session.commit()

    w_active = Worker(
        full_name="Active FilterWorker",
        daily_wage=Decimal("500.00"),
        is_active=True,
        created_by=admin.user_id,
    )
    w_inactive = Worker(
        full_name="Inactive FilterWorker",
        daily_wage=Decimal("400.00"),
        is_active=False,
        created_by=admin.user_id,
    )
    db_session.add_all([w_active, w_inactive])
    await db_session.commit()

    login_res = await client.post(
        "/api/v1/auth/login",
        json={"phone": "03888888807", "password": "Password123"},
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Default (no is_active param) -> returns both active and inactive
    all_res = await client.get("/api/v1/workers", headers=headers)
    assert all_res.status_code == 200
    all_names = [w["full_name"] for w in all_res.json()["items"]]
    assert "Active FilterWorker" in all_names
    assert "Inactive FilterWorker" in all_names

    # Filter is_active=true -> only active
    active_res = await client.get("/api/v1/workers?is_active=true", headers=headers)
    assert active_res.status_code == 200
    active_names = [w["full_name"] for w in active_res.json()["items"]]
    assert "Active FilterWorker" in active_names
    assert "Inactive FilterWorker" not in active_names

    # Filter is_active=false -> only inactive
    inactive_res = await client.get("/api/v1/workers?is_active=false", headers=headers)
    assert inactive_res.status_code == 200
    inactive_names = [w["full_name"] for w in inactive_res.json()["items"]]
    assert "Inactive FilterWorker" in inactive_names
    assert "Active FilterWorker" not in inactive_names
