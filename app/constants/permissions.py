"""Permission string constants for CSMS.

Defines namespaced permission identifiers used by the RBAC layer.
Each constant maps to one guarded action in the system.

Convention: ``PERM_<RESOURCE>_<ACTION>``

Per 02_BACKEND_RULES.md §10 Authorization and
CSMS_SPEC.md §5 User Roles.
"""

# ─── User management ─────────────────────────────────────────────────────────

PERM_USERS_CREATE = "users:create"
PERM_USERS_READ = "users:read"
PERM_USERS_UPDATE = "users:update"
PERM_USERS_DEACTIVATE = "users:deactivate"

# ─── Site management ─────────────────────────────────────────────────────────

PERM_SITES_CREATE = "sites:create"
PERM_SITES_READ = "sites:read"
PERM_SITES_UPDATE = "sites:update"
PERM_SITES_ARCHIVE = "sites:archive"
PERM_SITES_ASSIGN_SUPERVISOR = "sites:assign_supervisor"

# ─── Worker management ───────────────────────────────────────────────────────

PERM_WORKERS_CREATE = "workers:create"
PERM_WORKERS_READ = "workers:read"
PERM_WORKERS_UPDATE = "workers:update"
PERM_WORKERS_DEACTIVATE = "workers:deactivate"

# ─── Attendance ──────────────────────────────────────────────────────────────

PERM_ATTENDANCE_MARK = "attendance:mark"
PERM_ATTENDANCE_READ = "attendance:read"
PERM_ATTENDANCE_VERIFY = "attendance:verify"  # admin only

# ─── Expenses ────────────────────────────────────────────────────────────────

PERM_EXPENSES_CREATE = "expenses:create"
PERM_EXPENSES_READ = "expenses:read"

# ─── Supervisor wallet ───────────────────────────────────────────────────────

PERM_WALLET_CREDIT = "wallet:credit"
PERM_WALLET_DEBIT = "wallet:debit"
PERM_WALLET_READ = "wallet:read"

# ─── Worker payments ─────────────────────────────────────────────────────────

PERM_PAYMENTS_CREATE = "payments:create"
PERM_PAYMENTS_READ = "payments:read"

# ─── Warehouse & Inventory ───────────────────────────────────────────────────

PERM_WAREHOUSE_MANAGE = "warehouse:manage"
PERM_WAREHOUSE_READ = "warehouse:read"
PERM_STOCK_TRANSFER = "stock:transfer"
PERM_STOCK_READ = "stock:read"

# ─── Purchases (normal driver) ───────────────────────────────────────────────

PERM_PURCHASES_CREATE = "purchases:create"
PERM_PURCHASES_READ = "purchases:read"

# ─── Driver logs ─────────────────────────────────────────────────────────────

PERM_AJAX_LOG_CREATE = "ajax_log:create"
PERM_HITACHI_LOG_CREATE = "hitachi_log:create"
PERM_DRIVER_LOGS_READ = "driver_logs:read"

# ─── Reports & dashboard ─────────────────────────────────────────────────────

PERM_REPORTS_READ = "reports:read"
PERM_DASHBOARD_READ = "dashboard:read"
