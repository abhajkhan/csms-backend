"""Central re-export point for FastAPI dependencies.

Endpoint modules import from here so that the import path stays stable even
if the underlying implementation moves between dependency modules::

    from app.api.deps import get_db, get_current_active_user, require_admin

Per 02_BACKEND_RULES.md §4 Dependency Injection.
"""

# ─── Database ─────────────────────────────────────────────────────────────────
from app.db.session import get_db

# ─── Authentication ───────────────────────────────────────────────────────────
from app.dependencies.auth import get_current_active_user, get_current_user

# ─── Pagination ───────────────────────────────────────────────────────────────
from app.dependencies.pagination import get_pagination

# ─── Permissions ─────────────────────────────────────────────────────────────
from app.dependencies.permissions import require_permission

# ─── Role guards ─────────────────────────────────────────────────────────────
from app.dependencies.roles import (
    require_admin,
    require_admin_or_supervisor,
    require_ajax_driver,
    require_driver,
    require_hitachi_driver,
    require_normal_driver,
    require_supervisor,
)

__all__ = [
    # DB
    "get_db",
    # Auth
    "get_current_user",
    "get_current_active_user",
    # Pagination
    "get_pagination",
    # Permissions
    "require_permission",
    # Role guards
    "require_admin",
    "require_supervisor",
    "require_admin_or_supervisor",
    "require_driver",
    "require_ajax_driver",
    "require_hitachi_driver",
    "require_normal_driver",
]
