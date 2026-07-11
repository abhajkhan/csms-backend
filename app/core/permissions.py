"""RBAC permission utilities for CSMS.

Provides **pure functions** for role and driver-type checks.
These functions take primitive values (strings/enums) and return booleans —
they have no side effects and no database access.

The FastAPI dependency layer (``app.dependencies.roles``) will build on top
of these helpers once auth is implemented in Phase 1.

Per 02_BACKEND_RULES.md §9 Authorization and
Construction_System_Design_v2.md §3 User Roles.

Usage (in a service)::

    from app.core.permissions import can_record_expenses

    if not can_record_expenses(current_user.role):
        raise AuthorizationException()
"""

from app.constants.enums import DriverType, UserRole
from app.constants.roles import (
    AJAX_LOG_DRIVER_TYPES,
    ATTENDANCE_MARK_ROLES,
    ATTENDANCE_VERIFY_ROLES,
    EXPENSE_RECORD_ROLES,
    HITACHI_LOG_DRIVER_TYPES,
    PURCHASE_DRIVER_TYPES,
    PURCHASE_ROLES,
    REPORTING_ROLES,
    SALARY_SETTLEMENT_ROLES,
    SITE_MANAGEMENT_ROLES,
    STOCK_TRANSFER_ROLES,
    USER_MANAGEMENT_ROLES,
    WALLET_READ_ROLES,
    WALLET_ROLES,
    WAREHOUSE_MANAGEMENT_ROLES,
    WORKER_MANAGEMENT_ROLES,
)

# ─── Low-level role checks ────────────────────────────────────────────────────


def has_role(role: str | UserRole, *allowed: UserRole) -> bool:
    """Return ``True`` if *role* is in *allowed*.

    Args:
        role:    The user's role string or ``UserRole`` enum member.
        allowed: One or more ``UserRole`` values that grant access.

    Returns:
        ``True`` when the role matches, ``False`` otherwise.
    """
    try:
        return UserRole(role) in set(allowed)
    except ValueError:
        return False


def is_admin(role: str | UserRole) -> bool:
    """Return ``True`` when the user is an admin."""
    return has_role(role, UserRole.ADMIN)


def is_supervisor(role: str | UserRole) -> bool:
    """Return ``True`` when the user is a supervisor."""
    return has_role(role, UserRole.SUPERVISOR)


def is_driver(role: str | UserRole) -> bool:
    """Return ``True`` when the user is any driver type."""
    return has_role(role, UserRole.DRIVER)


# ─── Driver sub-type checks ───────────────────────────────────────────────────


def has_driver_type(
    role: str | UserRole,
    driver_type: str | DriverType | None,
    *allowed: DriverType,
) -> bool:
    """Return ``True`` when the user is a driver **and** matches *allowed*.

    Args:
        role:        The user's top-level role.
        driver_type: The user's driver sub-type (``None`` for non-drivers).
        allowed:     Driver sub-types that grant access.

    Returns:
        ``True`` only when both the role is ``DRIVER`` and the sub-type matches.
    """
    if not is_driver(role) or driver_type is None:
        return False
    try:
        return DriverType(driver_type) in set(allowed)
    except ValueError:
        return False


def is_ajax_driver(
    role: str | UserRole,
    driver_type: str | DriverType | None,
) -> bool:
    """Return ``True`` when the user is an Ajax driver."""
    return has_driver_type(role, driver_type, DriverType.AJAX)


def is_hitachi_driver(
    role: str | UserRole,
    driver_type: str | DriverType | None,
) -> bool:
    """Return ``True`` when the user is a Hitachi driver."""
    return has_driver_type(role, driver_type, DriverType.HITACHI)


def is_normal_driver(
    role: str | UserRole,
    driver_type: str | DriverType | None,
) -> bool:
    """Return ``True`` when the user is a Normal driver."""
    return has_driver_type(role, driver_type, DriverType.NORMAL)


# ─── Feature-level capability checks ─────────────────────────────────────────


def can_manage_users(role: str | UserRole) -> bool:
    """Return ``True`` when the role can create/edit user accounts."""
    return UserRole(role) in USER_MANAGEMENT_ROLES if _valid(role) else False


def can_manage_sites(role: str | UserRole) -> bool:
    """Return ``True`` when the role can create/edit sites."""
    return UserRole(role) in SITE_MANAGEMENT_ROLES if _valid(role) else False


def can_manage_workers(role: str | UserRole) -> bool:
    """Return ``True`` when the role can register or edit workers."""
    return UserRole(role) in WORKER_MANAGEMENT_ROLES if _valid(role) else False


def can_mark_attendance(role: str | UserRole) -> bool:
    """Return ``True`` when the role can submit attendance records."""
    return UserRole(role) in ATTENDANCE_MARK_ROLES if _valid(role) else False


def can_verify_attendance(role: str | UserRole) -> bool:
    """Return ``True`` when the role can verify supervisor attendance (admin)."""
    return UserRole(role) in ATTENDANCE_VERIFY_ROLES if _valid(role) else False


def can_record_expenses(role: str | UserRole) -> bool:
    """Return ``True`` when the role can record site expenses (supervisor)."""
    return UserRole(role) in EXPENSE_RECORD_ROLES if _valid(role) else False


def can_manage_wallet(role: str | UserRole) -> bool:
    """Return ``True`` when the role can credit/debit the wallet (supervisor)."""
    return UserRole(role) in WALLET_ROLES if _valid(role) else False


def can_read_wallet(role: str | UserRole) -> bool:
    """Return ``True`` when the role can view wallet history."""
    return UserRole(role) in WALLET_READ_ROLES if _valid(role) else False


def can_manage_warehouse(role: str | UserRole) -> bool:
    """Return ``True`` when the role can manage warehouse records (admin)."""
    return UserRole(role) in WAREHOUSE_MANAGEMENT_ROLES if _valid(role) else False


def can_transfer_stock(role: str | UserRole) -> bool:
    """Return ``True`` when the role can initiate stock transfers (supervisor)."""
    return UserRole(role) in STOCK_TRANSFER_ROLES if _valid(role) else False


def can_record_purchase(role: str | UserRole) -> bool:
    """Return ``True`` when the role can record normal-driver purchases."""
    return UserRole(role) in PURCHASE_ROLES if _valid(role) else False


def can_submit_ajax_log(
    role: str | UserRole,
    driver_type: str | DriverType | None,
) -> bool:
    """Return ``True`` when the user can submit an Ajax driver log."""
    return has_driver_type(role, driver_type, *AJAX_LOG_DRIVER_TYPES)


def can_submit_hitachi_log(
    role: str | UserRole,
    driver_type: str | DriverType | None,
) -> bool:
    """Return ``True`` when the user can submit a Hitachi driver log."""
    return has_driver_type(role, driver_type, *HITACHI_LOG_DRIVER_TYPES)


def can_submit_purchase(
    role: str | UserRole,
    driver_type: str | DriverType | None,
) -> bool:
    """Return ``True`` when the user can submit a purchase as a Normal driver."""
    return has_driver_type(role, driver_type, *PURCHASE_DRIVER_TYPES)


def can_settle_salary(role: str | UserRole) -> bool:
    """Return ``True`` when the role can process salary settlements (admin)."""
    return UserRole(role) in SALARY_SETTLEMENT_ROLES if _valid(role) else False


def can_view_reports(role: str | UserRole) -> bool:
    """Return ``True`` when the role has access to reporting endpoints (admin)."""
    return UserRole(role) in REPORTING_ROLES if _valid(role) else False


# ─── Internal helpers ─────────────────────────────────────────────────────────


def _valid(role: str | UserRole) -> bool:
    """Return ``True`` when *role* is a recognised ``UserRole`` value."""
    try:
        UserRole(role)
        return True
    except ValueError:
        return False
