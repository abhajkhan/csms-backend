"""Domain enum constants for CSMS.

All enum values are sourced directly from Construction_System_Design_v2.md.

Using ``str`` as the mixin ensures:
    - Values serialise to plain strings in JSON (Pydantic / FastAPI).
    - Values can be stored as VARCHAR in PostgreSQL without a separate type.
    - Enum members compare equal to their raw string values.

Per 02_BACKEND_RULES.md §16 Naming Conventions.
"""

from enum import Enum

# ─── User & Identity ─────────────────────────────────────────────────────────


class UserRole(str, Enum):
    """Top-level role for every account in the system.

    Design ref: Construction_System_Design_v2.md §4.1 Users.
    """

    ADMIN = "admin"
    SUPERVISOR = "supervisor"
    DRIVER = "driver"


class DriverType(str, Enum):
    """Sub-type that differentiates the three driver roles.

    Only meaningful when ``Users.role == UserRole.DRIVER``.
    Design ref: Construction_System_Design_v2.md §2.1.
    """

    HITACHI = "hitachi"
    AJAX = "ajax"
    NORMAL = "normal"


# ─── Sites ───────────────────────────────────────────────────────────────────


class SiteStatus(str, Enum):
    """Lifecycle status of a construction site.

    Design ref: Construction_System_Design_v2.md §4.2 Site.
    """

    ACTIVE = "active"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"


# ─── Attendance ───────────────────────────────────────────────────────────────


class LabourType(str, Enum):
    """Discriminator for the polymorphic ``Attendance.labour_id`` column.

    Design ref: Construction_System_Design_v2.md §4.5 Attendance.
    """

    USER = "USER"
    WORKER = "WORKER"


class AttendanceStatus(str, Enum):
    """Daily attendance state for any labour record.

    Design ref: Construction_System_Design_v2.md §4.5 Attendance.
    """

    PRESENT = "present"
    ABSENT = "absent"
    HALF_DAY = "half_day"


# ─── Wallet ───────────────────────────────────────────────────────────────────


class TxnType(str, Enum):
    """Transaction direction in the supervisor balance ledger.

    Design ref: Construction_System_Design_v2.md §4.6 SupervisorBalanceLog.
    """

    CREDIT = "credit"
    DEBIT = "debit"


class PaymentType(str, Enum):
    """Category of a worker payment record.

    Design ref: Construction_System_Design_v2.md §4.7 WorkerPayment.
    """

    ADVANCE = "advance"
    SETTLEMENT = "settlement"


# ─── Expenses ────────────────────────────────────────────────────────────────


class ExpenseType(str, Enum):
    """Source category of an expense entry.

    Design ref: Construction_System_Design_v2.md §4.8 Expense, §2.5.
    """

    MATERIAL_TRANSFER = "material_transfer"
    CASH_PURCHASE = "cash_purchase"
    DRIVER_MATERIAL = "driver_material"
    DRIVER_BATA = "driver_bata"
    DRIVER_VEHICLE_RENT = "driver_vehicle_rent"
    AJAX_SERVICE = "ajax_service"
    HITACHI_SERVICE = "hitachi_service"
    MISC = "misc"


class ReferenceType(str, Enum):
    """Source table that an expense's ``reference_id`` points to.

    Design ref: Construction_System_Design_v2.md §4.8 Expense, §2.5.
    """

    STOCK_MOVEMENT = "stock_movement"
    PURCHASE = "purchase"
    AJAX_LOG = "ajax_log"
    HITACHI_LOG = "hitachi_log"


# ─── Warehouse & Inventory ────────────────────────────────────────────────────


class MovementType(str, Enum):
    """Direction of a warehouse stock movement.

    Design ref: Construction_System_Design_v2.md §4.14 StockMovement.
    """

    IN = "IN"
    OUT = "OUT"


class ItemCategory(str, Enum):
    """Material category for warehouse items.

    Design ref: Construction_System_Design_v2.md §4.12 WarehouseItem.
    """

    CEMENT = "cement"
    METAL = "metal"
    SAND = "sand"
    AGGREGATE = "aggregate"
    WOOD = "wood"
    OTHER = "other"


# ─── Purchases ───────────────────────────────────────────────────────────────


class DestinationType(str, Enum):
    """Destination of a normal-driver purchase.

    Design ref: Construction_System_Design_v2.md §4.15 Purchase.
    """

    SITE = "site"
    WAREHOUSE = "warehouse"


class VehicleType(str, Enum):
    """Vehicle arrangement for a normal-driver purchase trip.

    ``OWN``   — driver uses their own vehicle; bata = vehicle_rent × 0.30.
    ``OUTER`` — an external vehicle is hired; rent stored as separate expense.
    ``NONE``  — no vehicle cost applies.

    Design ref: Construction_System_Design_v2.md §4.15 Purchase, §8 Normal Driver Bata.
    """

    OWN = "own"
    OUTER = "outer"
    NONE = "none"
