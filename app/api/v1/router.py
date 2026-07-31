"""API v1 router.

Aggregates all endpoint routers under the ``/api/v1`` prefix per CSMS_SPEC.md §11.7.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    ajax_logs,
    attendance,
    auth,
    dashboard,
    expenses,
    hitachi_logs,
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

# ─── Driver Logs ─────────────────────────────────────────────────────────────
api_router.include_router(
    ajax_logs.router, prefix="/ajax-logs", tags=["Ajax Driver Logs"]
)
api_router.include_router(
    hitachi_logs.router, prefix="/hitachi-logs", tags=["Hitachi Driver Logs"]
)

# ─── Reports ─────────────────────────────────────────────────────────────────
api_router.include_router(
    reports.router, prefix="/reports", tags=["Reports"]
)

# ─── Dashboard ───────────────────────────────────────────────────────────────
api_router.include_router(
    dashboard.router, prefix="/dashboard", tags=["Dashboard"]
)
