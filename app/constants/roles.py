"""Role-grouping constants for CSMS.

Defines which roles and driver-types are allowed for each system capability.
These frozensets are used by ``app.core.permissions`` and by the RBAC
dependency layer.

Per Construction_System_Design_v2.md §3 User Roles and §7 Role Functions.
"""

from app.constants.enums import DriverType, UserRole

# ─── All members ──────────────────────────────────────────────────────────────

ALL_ROLES: frozenset[UserRole] = frozenset(UserRole)
ALL_DRIVER_TYPES: frozenset[DriverType] = frozenset(DriverType)

# ─── Feature-level role groups ────────────────────────────────────────────────

#: Roles that can create / edit / deactivate user accounts.
USER_MANAGEMENT_ROLES: frozenset[UserRole] = frozenset({UserRole.ADMIN})

#: Roles that can register, edit, or deactivate workers.
#: Design ref: §7.1 Admin §Worker Management / §7.2 Supervisor §Worker Management.
WORKER_MANAGEMENT_ROLES: frozenset[UserRole] = frozenset(
    {UserRole.ADMIN, UserRole.SUPERVISOR}
)

#: Roles that can create or edit construction sites and assign supervisors.
SITE_MANAGEMENT_ROLES: frozenset[UserRole] = frozenset({UserRole.ADMIN})

#: Roles that can mark attendance for workers.
ATTENDANCE_MARK_ROLES: frozenset[UserRole] = frozenset(
    {UserRole.SUPERVISOR, UserRole.DRIVER}
)

#: The only role that may verify or invalidate supervisor attendance records.
ATTENDANCE_VERIFY_ROLES: frozenset[UserRole] = frozenset({UserRole.ADMIN})

#: Roles that can record site expenses.
EXPENSE_RECORD_ROLES: frozenset[UserRole] = frozenset({UserRole.SUPERVISOR})

#: Roles that can credit / debit the supervisor wallet.
WALLET_ROLES: frozenset[UserRole] = frozenset({UserRole.SUPERVISOR})

#: Roles with read access to all wallet history.
WALLET_READ_ROLES: frozenset[UserRole] = frozenset(
    {UserRole.ADMIN, UserRole.SUPERVISOR}
)

#: Roles that can manage warehouse records and the item catalogue.
WAREHOUSE_MANAGEMENT_ROLES: frozenset[UserRole] = frozenset({UserRole.ADMIN})

#: Roles that can initiate stock-movement transfers to a site.
STOCK_TRANSFER_ROLES: frozenset[UserRole] = frozenset({UserRole.SUPERVISOR})

#: Role that can record Normal-driver purchases.
PURCHASE_ROLES: frozenset[UserRole] = frozenset({UserRole.DRIVER})

#: Driver sub-types allowed to submit Ajax log entries.
AJAX_LOG_DRIVER_TYPES: frozenset[DriverType] = frozenset({DriverType.AJAX})

#: Driver sub-types allowed to submit Hitachi log entries.
HITACHI_LOG_DRIVER_TYPES: frozenset[DriverType] = frozenset({DriverType.HITACHI})

#: Driver sub-types allowed to submit Purchase entries.
PURCHASE_DRIVER_TYPES: frozenset[DriverType] = frozenset({DriverType.NORMAL})

#: The only role that may record weekend salary settlements.
SALARY_SETTLEMENT_ROLES: frozenset[UserRole] = frozenset({UserRole.ADMIN})

#: Roles with access to reporting endpoints.
REPORTING_ROLES: frozenset[UserRole] = frozenset({UserRole.ADMIN})
