"""API v1 router.

Aggregates all endpoint routers under the ``/api/v1`` prefix defined in
``app.main``.  Only add a router here once the corresponding endpoint module
has at least one route implemented.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    attendance,
    auth,
    dashboard,
    drivers,
    expenses,
    purchases,
    reports,
    sites,
    users,
    warehouse,
    workers,
)

api_router = APIRouter()

# ─── Authentication ──────────────────────────────────────────────────────────
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# ─── User Management ─────────────────────────────────────────────────────────
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# ─── Site Management ─────────────────────────────────────────────────────────
api_router.include_router(sites.router, prefix="/sites", tags=["Sites"])

# ─── Worker Management ───────────────────────────────────────────────────────
api_router.include_router(workers.router, prefix="/workers", tags=["Workers"])

# ─── Attendance ──────────────────────────────────────────────────────────────
api_router.include_router(
    attendance.router, prefix="/attendance", tags=["Attendance"]
)

# ─── Expenses ────────────────────────────────────────────────────────────────
api_router.include_router(
    expenses.router, prefix="/expenses", tags=["Expenses"]
)

# ─── Warehouse & Inventory ───────────────────────────────────────────────────
api_router.include_router(
    warehouse.router, prefix="", tags=["Warehouse"]
)

# ─── Purchases ───────────────────────────────────────────────────────────────
api_router.include_router(
    purchases.router, prefix="/purchases", tags=["Purchases"]
)

# ─── Driver Logs & Worker Payments ───────────────────────────────────────────
api_router.include_router(
    drivers.router, prefix="", tags=["Drivers"]
)

# ─── Reports ─────────────────────────────────────────────────────────────────
api_router.include_router(
    reports.router, prefix="/reports", tags=["Reports"]
)

# ─── Dashboard ───────────────────────────────────────────────────────────────
api_router.include_router(
    dashboard.router, prefix="/dashboard", tags=["Dashboard"]
)
