"""Permission-based FastAPI dependency.

Provides ``PermissionChecker`` — a fine-grained dependency factory that
enforces specific permission strings (defined in ``app.constants.permissions``)
by mapping them to the ``core.permissions`` utility functions.

Unlike ``RoleChecker`` (which checks the user's role directly),
``PermissionChecker`` uses the capability-level predicates in
``app.core.permissions`` to grant access.  This keeps permission logic
in one place and avoids scattering role checks across endpoints.

Usage::

    from app.dependencies.permissions import require_permission
    from app.constants.permissions import PERM_WORKERS_CREATE

    @router.post("/workers", status_code=201)
    def create_worker(
        current_user: CurrentUserResponse = Depends(
            require_permission(PERM_WORKERS_CREATE)
        ),
    ):
        ...

Per 02_BACKEND_RULES.md §9 Authorization.
"""

from __future__ import annotations

from fastapi import Depends

from app.constants import permissions as perms
from app.core import permissions as perm_utils
from app.core.exceptions import AuthorizationException
from app.dependencies.auth import get_current_active_user
from app.schemas.user import CurrentUserResponse

# ─── Permission → capability function mapping ─────────────────────────────────

# Maps each permission constant to the ``core.permissions`` predicate that
# evaluates it.  All predicates are callables of the form:
#   (role: str, driver_type: str | None) -> bool
# or (role: str) -> bool

_SINGLE_ARG_MAP: dict[str, object] = {
    perms.PERM_USERS_CREATE: perm_utils.can_manage_users,
    perms.PERM_USERS_READ: perm_utils.can_manage_users,
    perms.PERM_USERS_UPDATE: perm_utils.can_manage_users,
    perms.PERM_USERS_DEACTIVATE: perm_utils.can_manage_users,
    perms.PERM_SITES_CREATE: perm_utils.can_manage_sites,
    perms.PERM_SITES_READ: perm_utils.can_manage_sites,
    perms.PERM_SITES_UPDATE: perm_utils.can_manage_sites,
    perms.PERM_SITES_ARCHIVE: perm_utils.can_manage_sites,
    perms.PERM_SITES_ASSIGN_SUPERVISOR: perm_utils.can_manage_sites,
    perms.PERM_WORKERS_CREATE: perm_utils.can_manage_workers,
    perms.PERM_WORKERS_READ: perm_utils.can_manage_workers,
    perms.PERM_WORKERS_UPDATE: perm_utils.can_manage_workers,
    perms.PERM_WORKERS_DEACTIVATE: perm_utils.can_manage_workers,
    perms.PERM_ATTENDANCE_MARK: perm_utils.can_mark_attendance,
    perms.PERM_ATTENDANCE_READ: perm_utils.can_mark_attendance,
    perms.PERM_ATTENDANCE_VERIFY: perm_utils.can_verify_attendance,
    perms.PERM_EXPENSES_CREATE: perm_utils.can_record_expenses,
    perms.PERM_EXPENSES_READ: perm_utils.can_record_expenses,
    perms.PERM_WALLET_CREDIT: perm_utils.can_manage_wallet,
    perms.PERM_WALLET_DEBIT: perm_utils.can_manage_wallet,
    perms.PERM_WALLET_READ: perm_utils.can_read_wallet,
    perms.PERM_PAYMENTS_CREATE: perm_utils.can_manage_workers,
    perms.PERM_PAYMENTS_READ: perm_utils.can_manage_workers,
    perms.PERM_WAREHOUSE_MANAGE: perm_utils.can_manage_warehouse,
    perms.PERM_WAREHOUSE_READ: perm_utils.can_manage_warehouse,
    perms.PERM_STOCK_TRANSFER: perm_utils.can_transfer_stock,
    perms.PERM_STOCK_READ: perm_utils.can_transfer_stock,
    perms.PERM_PURCHASES_CREATE: perm_utils.can_record_purchase,
    perms.PERM_PURCHASES_READ: perm_utils.can_record_purchase,
    perms.PERM_REPORTS_READ: perm_utils.can_view_reports,
    perms.PERM_DASHBOARD_READ: perm_utils.can_view_reports,
}

# Permissions that require both (role, driver_type) arguments.
_DUAL_ARG_MAP: dict[str, object] = {
    perms.PERM_AJAX_LOG_CREATE: perm_utils.can_submit_ajax_log,
    perms.PERM_HITACHI_LOG_CREATE: perm_utils.can_submit_hitachi_log,
    perms.PERM_DRIVER_LOGS_READ: perm_utils.can_submit_ajax_log,
}


class PermissionChecker:
    """Callable dependency that enforces a single permission string.

    On success, returns the ``CurrentUserResponse``.
    On failure, raises ``AuthorizationException`` (403).

    Args:
        permission: A ``PERM_*`` constant from ``app.constants.permissions``.
    """

    def __init__(self, permission: str) -> None:
        self._permission = permission

    async def __call__(
        self,
        current_user: CurrentUserResponse = Depends(get_current_active_user),
    ) -> CurrentUserResponse:
        """Enforce the permission.

        Args:
            current_user: Authenticated user from ``get_current_active_user``.

        Returns:
            The same ``CurrentUserResponse`` when access is granted.

        Raises:
            ``AuthorizationException`` (403): When the user lacks the permission.
        """
        role = current_user.role
        driver_type = current_user.driver_type

        granted = False

        if self._permission in _DUAL_ARG_MAP:
            fn = _DUAL_ARG_MAP[self._permission]
            granted = fn(role, driver_type)  # type: ignore[call-arg]
        elif self._permission in _SINGLE_ARG_MAP:
            fn = _SINGLE_ARG_MAP[self._permission]
            granted = fn(role)  # type: ignore[call-arg]
        else:
            # Unknown permission — deny by default.
            granted = False

        if not granted:
            raise AuthorizationException(
                f"You do not have the '{self._permission}' permission."
            )

        return current_user

    def __repr__(self) -> str:
        return f"PermissionChecker(permission='{self._permission}')"


def require_permission(permission: str) -> PermissionChecker:
    """Factory that returns a ``PermissionChecker`` for *permission*.

    Intended for one-off permission checks on individual endpoints.
    For common role groups, prefer the pre-built instances in
    ``app.dependencies.roles``.

    Args:
        permission: A ``PERM_*`` constant.

    Returns:
        A ``PermissionChecker`` instance usable as a FastAPI dependency.

    Example::

        Depends(require_permission(PERM_WORKERS_CREATE))
    """
    return PermissionChecker(permission)
