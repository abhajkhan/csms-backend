# Construction Site Management System (CSMS)
## Functional Specification

Version: 1.0 (Consolidated)
Status: Authoritative — this document is the sole functional specification for the project.

---

# 1. Overview

The Construction Site Management System (CSMS) is a role-based backend application that digitizes the daily operations of construction projects: labour management, attendance tracking, site expenses, warehouse inventory, material purchases, driver activity logging, supervisor wallet accounting, and worker salary settlement.

The system replaces paper- and spreadsheet-based workflows with a centralized platform. Its primary objective is accurate financial tracking, operational transparency, and data consistency across multiple construction sites.

---

# 2. Technology Stack

| Component | Technology |
|---|---|
| Language | Python 3.12+ |
| Framework | FastAPI (0.116.1) |
| Database | PostgreSQL |
| ORM | SQLAlchemy 2.0 (2.0.43), typed style |
| Migration | Alembic (1.16.4) |
| Validation | Pydantic v2 (2.11.7), pydantic-settings (2.10.1) |
| Authentication | JWT (python-jose[cryptography] 3.5.0), Refresh Tokens |
| Password Hashing | BCrypt (passlib[bcrypt] 1.7.4, bcrypt 4.1.3) |
| Testing | Pytest (8.4.1), pytest-asyncio, pytest-cov, faker, factory-boy |
| Code Quality | black, isort, ruff, mypy, pre-commit |
| DB Driver | psycopg[binary] 3.2.9, greenlet |
| HTTP Client | httpx |
| API Style | REST, JSON |
| Frontend (consumer) | Flutter |

No alternative frameworks, libraries, or architectural patterns should be introduced without explicit approval. Pillow is an optional dependency, included but inactive, for future image-handling needs; it is not required by any feature currently in scope.

---

# 3. System Architecture

The backend follows a strict layered architecture:

```
Flutter Client
      │
      ▼
REST API (FastAPI)
      │
      ▼
API Layer
      │
      ▼
Service Layer
      │
      ▼
Repository Layer
      │
      ▼
PostgreSQL Database
```

## 3.1 Layer Responsibilities

**API Layer**
- Receives HTTP requests, authenticates and authorizes the user, validates request shape via Pydantic schemas, calls services, and returns responses.
- Must never execute SQL, contain business logic, perform calculations, or update multiple entities directly.

**Service Layer**
- Implements all business rules, validates business conditions, coordinates repositories, manages transactions, and raises business-specific exceptions.
- Must never contain HTTP-specific logic, return HTTP responses, or access request objects directly.

**Repository Layer**
- Executes all SQLAlchemy queries: CRUD, filtering, pagination, joins.
- Must never contain business rules, perform authorization, or call other repositories.

**Model Layer**
- Defines SQLAlchemy ORM models representing database tables, relationships, and constraints only. No business logic.

**Schema Layer**
- Defines Pydantic request/response DTOs and validation rules. Only schemas are exposed outside the Service layer.

## 3.2 Dependency Injection

FastAPI dependency injection is used for: database sessions, current user resolution, permission checks, and pagination parameters. Dependencies are never instantiated manually inside route handlers.

## 3.3 Transactions

Transactions are managed exclusively inside the Service layer, using `session.begin()` or equivalent, with automatic rollback on failure. Repositories never commit transactions.

The following operations must always execute atomically, within a single transaction:

- Expense creation + Supervisor wallet debit (`SupervisorBalanceLog` entry)
- Worker advance (`WorkerPayment`) + Supervisor wallet debit
- Warehouse-to-site transfer (`StockMovement` OUT) + Expense creation (`material_transfer`)
- Ajax Driver Log creation + Expense creation (`ajax_service`)
- Hitachi Driver Log creation + Expense creation (`hitachi_service`)
- Normal Driver Purchase (destination = site) + creation of 1–3 linked Expense entries (`driver_material`, `driver_bata`, `driver_vehicle_rent`)
- `StockMovement` IN (warehouse) + `WarehouseStock` quantity update + (where procurement-related, see §8.6) `WarehouseItem.last_unit_price` update

---

# 4. Design Principles

- Clean Architecture and Separation of Concerns
- Repository Pattern and Service Layer Pattern
- Dependency Injection
- RESTful API Design (nouns, not verbs; plural resource paths)
- Atomic Database Transactions for all financially-linked operations
- Soft Delete for entities with historical significance
- Role-Based Access Control (RBAC)
- Type Safety (type hints on every function)
- Explicit, custom-exception-based error handling
- Each business module remains independent and communicates only through services

## 4.1 Non-Goals

The following are intentionally out of scope unless explicitly requested in a future revision of this document:

- Microservices, GraphQL, WebSockets, event-driven architecture
- Redis caching, Celery background workers
- Multi-tenancy, offline synchronization, multi-language support, plugin architecture
- Supervisor attendance verification/rejection workflow (see §8.2 for rationale)
- A structured `reference_type`/`reference_id` pair on `SupervisorBalanceLog` (see §6.6 for rationale)
- A dedicated "pending salary" endpoint beyond the salary report (see §11.7)
- A `movement_reason`/`source_type` field on `StockMovement` (see §8.6 for rationale)
- Role-based authorization rules for `POST /stock-movements` beyond standard RBAC — this is a known open item for a future revision, not resolved by this specification

---

# 5. User Roles

The system supports five operational roles, all stored in a single `Users` table (§6.1), differentiated by `role` and, for drivers, `driver_type`:

| Role | Summary |
|---|---|
| Admin | Full system access: accounts, sites, warehouse, workers, weekend salary settlements, reporting |
| Supervisor | Manages workers, marks attendance, records site expenses, handles material transfers, pays daily worker advances |
| Ajax Driver | Records daily mix count per site; system auto-calculates and logs the associated expense |
| Hitachi Driver | Records daily hours worked per site; system auto-calculates and logs the associated expense |
| Normal Driver | Records material purchases for sites or warehouse; logs vehicle rent; bata auto-calculated |

Client-provided role information is never trusted. Every protected endpoint reads role and permissions from the authenticated user (resolved server-side from the JWT), and every protected endpoint verifies permissions before executing business logic.

---

# 6. Database Schema

The system consists of 14 tables (see §8.2 for the removal of supervisor-attendance-verification columns from the original design).

## 6.1 Users

Central authentication and identity table. All user types are stored in a single table.

| Column | Type | Description |
|---|---|---|
| user_id | int PK | Unique identifier |
| role | enum | `admin`, `supervisor`, `driver` |
| driver_type | enum | `hitachi`, `ajax`, `normal`, `null` — null for admin and supervisor |
| full_name | varchar | Full name of the user |
| phone | varchar | Login identifier, must be unique |
| password_hash | varchar | Hashed password (BCrypt) |
| is_active | boolean | Soft delete — inactive users cannot log in |
| acc_balance | decimal | Running wallet balance — supervisors only; null for others |

## 6.2 Site

| Column | Type | Description |
|---|---|---|
| site_id | int PK | Unique identifier |
| site_name | varchar | Name of the construction site |
| location | varchar | Physical address or area |
| status | enum | `active`, `completed`, `on_hold` |
| created_at | datetime | Creation timestamp |
| created_by | int FK → Users | Must be admin |

## 6.3 SiteSupervisor

Junction table for many-to-many assignment between supervisors and sites. `is_active` allows reassignment without deleting history.

| Column | Type | Description |
|---|---|---|
| id | int PK | Unique identifier |
| site_id | int FK → Site | |
| supervisor_id | int FK → Users | Must be a supervisor |
| assigned_at | datetime | Date of assignment |
| is_active | boolean | Whether this assignment is currently active |

## 6.4 Workers

Labour records. Workers do not log into the system and have no fixed site — their site association is determined through Attendance.

| Column | Type | Description |
|---|---|---|
| worker_id | int PK | Unique identifier |
| full_name | varchar | Worker's full name |
| daily_wage | decimal | Standard daily wage rate |
| is_active | boolean | Soft delete flag |
| created_by | int FK → Users | Admin or supervisor who registered the worker |

## 6.5 Attendance

Polymorphic attendance table covering both Users (supervisors, drivers) and Workers via `labour_type` + `labour_id`.

| Column | Type | Description |
|---|---|---|
| attendance_id | int PK | Unique identifier |
| date | date | Date of attendance |
| labour_type | enum | `USER`, `WORKER` — determines which table `labour_id` references |
| labour_id | int | References Users.user_id or Workers.worker_id depending on labour_type |
| site_id | int FK → Site | Nullable for drivers |
| status | enum | `present`, `absent`, `half_day` |

The unique index is on `(labour_type, labour_id, site_id, date)`, allowing a worker to be marked `half_day` on two different sites on the same date. `labour_type`/`labour_id` is not enforceable as a database foreign key across two tables; referential integrity for this column pair is the responsibility of the Service layer.

Supervisor attendance carries no verification state and requires no admin action — it is recorded and stored identically to any other attendance record.

## 6.6 SupervisorBalanceLog

Ledger of every credit and debit to a supervisor's wallet.

| Column | Type | Description |
|---|---|---|
| log_id | int PK | Unique identifier |
| supervisor_id | int FK → Users | |
| txn_type | enum | `credit`, `debit` |
| amount | decimal | Transaction amount |
| note | varchar | Free-text description, e.g. "Admin cash received", "Expense: cement bags" |
| created_at | datetime | Timestamp |

This table intentionally has no structured `reference_type`/`reference_id` link to its source record. The `note` field is the sole descriptive record of each transaction. This is a deliberate design decision, not an omission — see §8.1 for the corresponding business rule and rationale.

## 6.7 WorkerPayment

Tracks all payments to workers.

| Column | Type | Description |
|---|---|---|
| payment_id | int PK | Unique identifier |
| worker_id | int FK → Workers | |
| paid_by | int FK → Users | Supervisor for advances, admin for settlements |
| amount | decimal | Amount paid |
| payment_type | enum | `advance`, `settlement` |
| paid_at | datetime | Timestamp of payment |
| note | varchar | Optional note |

## 6.8 Expense

Central table recording every cost incurred at a site.

| Column | Type | Description |
|---|---|---|
| expense_id | int PK | Unique identifier |
| date | date | Date the expense occurred |
| recorded_at | datetime | Timestamp of entry |
| amount | decimal | Expense amount |
| site_id | int FK → Site | |
| recorded_by | int FK → Users | |
| expense_type | enum | `material_transfer`, `cash_purchase`, `driver_material`, `driver_bata`, `driver_vehicle_rent`, `ajax_service`, `hitachi_service`, `misc` |
| reference_id | int | Optional — links to StockMovement, Purchase, AjaxDriverLog, or HitachiDriverLog |
| reference_type | enum | `stock_movement`, `purchase`, `ajax_log`, `hitachi_log`, `null` |
| description | text | Free-text description |

## 6.9 AjaxDriverLog

Daily mix count per Ajax driver per site. On save, the system auto-calculates `total_amount` and creates a linked Expense.

| Column | Type | Description |
|---|---|---|
| log_id | int PK | Unique identifier |
| driver_id | int FK → Users | Must be `driver_type = ajax` |
| site_id | int FK → Site | |
| date | date | Date of work |
| num_mixes | int | Number of mixes completed |
| rate_per_mix | decimal | Snapshot of rate at time of entry |
| total_amount | decimal | `num_mixes × rate_per_mix`, calculated and stored at save time |
| expense_id | int FK → Expense | Auto-created on save |
| note | varchar | Optional remarks |

## 6.10 HitachiDriverLog

Daily hours worked per Hitachi driver per site. On save, the system auto-calculates `total_amount` and creates a linked Expense.

| Column | Type | Description |
|---|---|---|
| log_id | int PK | Unique identifier |
| driver_id | int FK → Users | Must be `driver_type = hitachi` |
| site_id | int FK → Site | |
| date | date | Date of work |
| hours_worked | decimal | Number of hours worked |
| hourly_rate | decimal | Snapshot of rate at time of entry |
| total_amount | decimal | `hours_worked × hourly_rate`, calculated and stored at save time |
| expense_id | int FK → Expense | Auto-created on save |
| note | varchar | Optional remarks |

## 6.11 Warehouse

Physical storage location. Multiple warehouses are supported.

| Column | Type | Description |
|---|---|---|
| warehouse_id | int PK | Unique identifier |
| name | varchar | Warehouse name |
| location | varchar | Physical location |

## 6.12 WarehouseItem

Global catalog of material types, not tied to a specific warehouse.

| Column | Type | Description |
|---|---|---|
| item_id | int PK | Unique identifier |
| name | varchar | e.g. Cement, GSP Sand, Steel Rod |
| description | text | Optional details (grade, specification) |
| category | enum | `cement`, `metal`, `sand`, `aggregate`, `wood`, `other` |
| unit | varchar | `kg`, `tonne`, `bag`, `cubic_meter`, `piece` |
| last_unit_price | decimal | Price per unit from the most recent procurement — see §8.6 for the exact update trigger |

## 6.13 WarehouseStock

Current available quantity of each item at each warehouse. One row per item per warehouse.

| Column | Type | Description |
|---|---|---|
| stock_id | int PK | Unique identifier |
| warehouse_id | int FK → Warehouse | |
| item_id | int FK → WarehouseItem | |
| quantity | decimal | Current available quantity |
| last_updated | datetime | Timestamp of last stock change |

## 6.14 StockMovement

Every inventory movement. `IN` movements are procurement deliveries to warehouse. `OUT` movements are materials issued to a site.

| Column | Type | Description |
|---|---|---|
| movement_id | int PK | Unique identifier |
| warehouse_id | int FK → Warehouse | |
| item_id | int FK → WarehouseItem | |
| movement_type | enum | `IN`, `OUT` |
| quantity | decimal | Quantity moved |
| unit_price | decimal | Price per unit at time of movement (snapshot) |
| total_amount | decimal | `quantity × unit_price` |
| movement_date | datetime | When the movement occurred |
| site_id | int FK → Site | Nullable; populated for OUT movements |
| reference | varchar | PO number, delivery note, or other reference |
| created_by | int FK → Users | |

Warehouse-to-warehouse transfers are not supported; items move only from warehouse to site.

## 6.15 Purchase

Records all Normal Driver purchase transactions. Ajax and Hitachi drivers do not use this table.

| Column | Type | Description |
|---|---|---|
| purchase_id | int PK | Unique identifier |
| purchased_by | int FK → Users | Must be `driver_type = normal` |
| item_id | int FK → WarehouseItem | |
| site_id | int FK → Site | Nullable when `destination_type = warehouse` |
| warehouse_id | int FK → Warehouse | Nullable when `destination_type = site` |
| destination_type | enum | `site`, `warehouse` |
| quantity | decimal | Quantity purchased |
| unit_price | decimal | Price per unit |
| total_amount | decimal | `quantity × unit_price` |
| unit | varchar | Unit of measurement |
| purchased_from | varchar | Vendor name or source location |
| vehicle_type | enum | `own`, `outer`, `none` |
| vehicle_rent | decimal | Rent amount — bata = `vehicle_rent × 0.30` if `vehicle_type = own` |
| purchase_date | datetime | Date and time of purchase |
| note | text | Optional remarks |

---

# 7. Entity Relationships

**Users**
- One Supervisor is assigned to many Sites through SiteSupervisor
- One Supervisor has many SupervisorBalanceLog entries
- One Supervisor makes advance WorkerPayments; one Admin makes settlement WorkerPayments
- One User records many Expenses
- One Ajax Driver has many AjaxDriverLog entries
- One Hitachi Driver has many HitachiDriverLog entries
- One Normal Driver makes many Purchases
- One Admin or Supervisor creates many Workers

**Site**
- One Site has many Supervisors through SiteSupervisor
- One Site has many Attendance records
- One Site has many Expense records
- One Site receives many StockMovements (OUT)
- One Site is referenced by many AjaxDriverLog and HitachiDriverLog entries
- One Site can be the destination for many Purchases

**Workers**
- Workers have no fixed site — association is through Attendance only
- One Worker receives many WorkerPayments (advances and settlements)
- One Worker has many Attendance records across multiple sites, same or different days

**Driver Logs & Expenses**
- Each AjaxDriverLog entry creates exactly one Expense (`ajax_service`) via `expense_id`
- Each HitachiDriverLog entry creates exactly one Expense (`hitachi_service`) via `expense_id`
- Each Purchase to a site creates 1 to 3 Expense entries (material, bata, vehicle rent)
- `Expense.reference_id` + `reference_type` traces any expense back to its source record

**Warehouse & Inventory**
- One Warehouse has many WarehouseStock entries (one per item it holds)
- One WarehouseItem exists across many Warehouses via WarehouseStock
- StockMovement OUT links to a site and auto-creates a `material_transfer` Expense
- StockMovement IN, when procurement-related, updates `WarehouseItem.last_unit_price` (§8.6)

---

# 8. Business Rules

## 8.1 Supervisor Wallet

- One shared wallet per supervisor covers all their assigned sites.
- Every expense and worker advance debits the wallet.
- `acc_balance` on Users is the running total; `SupervisorBalanceLog` is the transaction history.
- Both must be written atomically — if either write fails, both roll back.
- Weekend salary settlements do not deduct from the supervisor wallet.
- `SupervisorBalanceLog` uses a free-text `note` field only, with no structured link back to the source record. This is intentional: no feature in this specification requires programmatic reconciliation between a ledger entry and its source, so a structured reference is not built. If a future feature requires it, it should be added at that time, scoped to that feature's concrete requirements.

## 8.2 Attendance

- Attendance is recorded identically for Workers, Supervisors, and all Driver types via the polymorphic `labour_type`/`labour_id` pattern.
- There is no supervisor-attendance verification, approval, or rejection workflow of any kind. Supervisor attendance carries no additional state beyond `status`, and no admin action is required or available for it.
- A worker may be marked `half_day` at two different sites on the same date; this is the only case where more than one attendance record for the same person may exist on the same date (see §8.5 for the salary-calculation implication and cap).

## 8.3 Driver Type Enforcement

- Only Ajax drivers (`driver_type = ajax`) may submit AjaxDriverLog entries.
- Only Hitachi drivers (`driver_type = hitachi`) may submit HitachiDriverLog entries.
- Only Normal drivers (`driver_type = normal`) may submit Purchase entries.
- This must be enforced at both the UI and API level; the API layer must never trust client-provided role or driver-type information.

## 8.4 Ajax & Hitachi Rate Snapshots

- `rate_per_mix` and `hourly_rate` are managed as application-level configuration, not database records, and are snapshotted into `AjaxDriverLog`/`HitachiDriverLog` at the time of entry.
- Changing the configured rate does not affect historical log records.
- `total_amount` is calculated and stored at save time and is never recalculated.

## 8.5 Worker Salary

- **Day-equivalent weighting:** attendance status contributes to salary as follows: `present = 1.0`, `half_day = 0.5`, `absent = 0.0`.
- **Pending balance formula:**
  ```
  Pending = (sum of day-equivalents across all attendance records for the worker × daily_wage) − sum of all advance payments
  ```
- **Per-date cap:** the sum of day-equivalents for a single worker on a single date must never exceed `1.0`. This permits the explicitly supported case of two `half_day` records on the same date at different sites (0.5 + 0.5 = 1.0) while preventing any combination of records from crediting more than one day's wage for a single calendar date. This is enforced at the point of attendance creation: before inserting a new record, the service sums existing day-equivalents for the same `(labour_type, labour_id, date)` and rejects the write if the total would exceed `1.0`. The check and the insert occur within the same transaction.
- Workers have no fixed site — salary is computed across all attendance records regardless of site.
- Admin views the pending balance per worker and marks workers as paid during settlement.
- Settlement cash is distributed outside the app; only the "Paid" action is recorded, as a `WorkerPayment` with `payment_type = settlement`. No wallet deduction occurs for settlements.

## 8.6 Normal Driver Bata

- Bata applies only when `vehicle_type = own`.
- Bata = `vehicle_rent × 0.30` — a fixed percentage; no distance/km tracking.
- Bata is stored as a separate `driver_bata` Expense entry, distinct from material cost.
- Outer vehicle rent is stored as a separate `driver_vehicle_rent` Expense entry.

## 8.6 Material Pricing and Procurement

- Warehouse-to-site transfers use `quantity × WarehouseItem.last_unit_price`.
- `StockMovement` stores a `unit_price` snapshot for historical accuracy on every movement, regardless of direction.
- `WarehouseItem.last_unit_price` is updated only on **procurement-related** `StockMovement(IN)` records. There are exactly two ways such a record can be created:
  1. **Admin bulk warehouse purchase** — Admin creates a `StockMovement(IN)` directly, with `created_by` set to the admin's `user_id`. This does not create a `Purchase` record; `Purchase` remains exclusively for Normal Drivers (§8.3).
  2. **Normal Driver purchase to warehouse** — a `Purchase` with `destination_type = warehouse` creates a `StockMovement(IN)` and increases `WarehouseStock`.
- No other mechanism currently in this specification creates a `StockMovement(IN)`. If a future feature introduces a non-procurement `IN` movement (for example, a stock-count correction or inventory audit adjustment), this rule must be revisited, and a way to distinguish movement sources will need to be introduced at that time. Until then, no additional field (such as a movement-reason or source-type column) is added to `StockMovement`, since no current feature requires the distinction to be made in the schema.

## 8.7 Transaction Integrity

The following must always be atomic:

- `WorkerPayment` (advance) + `SupervisorBalanceLog` debit
- Expense creation + `SupervisorBalanceLog` debit
- `StockMovement` OUT + Expense (`material_transfer`)
- `AjaxDriverLog` + Expense (`ajax_service`)
- `HitachiDriverLog` + Expense (`hitachi_service`)
- Normal Driver Purchase (destination = site) + linked Expense entries

---

# 9. System Workflows

## 9.1 System Setup (Admin)

1. **Create user accounts** — Admin creates supervisor, Ajax driver, Hitachi driver, and Normal driver accounts with the appropriate role and `driver_type`.
2. **Create sites** — Admin creates construction site records with name, location, and status.
3. **Assign supervisors to sites** — Admin assigns one or more supervisors to each site via SiteSupervisor.
4. **Set up warehouse and item catalog** — Admin adds warehouse records and creates WarehouseItem entries with category, unit, and initial pricing.
5. **Register workers** — Admin or supervisor registers workers with name and daily wage.

## 9.2 Daily Operations (Supervisor)

1. **Top up wallet** — Supervisor credits their own `acc_balance` when cash is received from admin (outside the app). A `SupervisorBalanceLog` credit entry is created.
2. **Mark attendance** — Supervisor marks attendance for workers and themselves. Workers may be `half_day` on two different sites on the same date, subject to the cap in §8.5.
3. **Record expenses** — Supervisor records each site expense. Each entry debits the supervisor wallet and creates a `SupervisorBalanceLog` entry, atomically.
4. **Transfer materials from warehouse** — Supervisor selects item and quantity. The system creates `StockMovement` OUT, reduces stock, and auto-creates a `material_transfer` Expense using `last_unit_price`.
5. **Pay worker advances** — Supervisor enters an advance amount per worker. `WorkerPayment` (advance) and the `SupervisorBalanceLog` debit are created atomically.

## 9.3 Ajax Driver Daily Flow

1. Driver selects the site worked on and enters the date.
2. Driver enters the number of mixes completed.
3. The system reads `rate_per_mix` from configuration, calculates `total_amount`, saves the `AjaxDriverLog`, and auto-creates an `ajax_service` Expense for the site, atomically.
4. Driver marks their own attendance for the day (not site-specific).

## 9.4 Hitachi Driver Daily Flow

1. Driver selects the site and enters the date.
2. Driver enters total hours worked.
3. The system reads `hourly_rate` from configuration, calculates `total_amount`, saves the `HitachiDriverLog`, and auto-creates a `hitachi_service` Expense for the site, atomically.
4. Driver marks their own attendance for the day (not site-specific).

## 9.5 Normal Driver Purchase Flow

1. Driver records a purchase: item, quantity, price, vendor, destination (site or warehouse), and vehicle details.
2. **Destination = Site** — the system auto-creates `driver_material` (purchase cost), `driver_bata` (if `vehicle_type = own`), and `driver_vehicle_rent` (if `vehicle_type = outer`) Expense entries. No stock is added to any warehouse.
3. **Destination = Warehouse** — the system creates `StockMovement` IN, increases `WarehouseStock`, and updates `WarehouseItem.last_unit_price` (procurement-related, per §8.6).
4. Driver marks their own attendance for the day.

## 9.6 Admin Bulk Warehouse Purchase

1. Admin records a large procurement purchase directly against a warehouse.
2. The system creates `StockMovement` IN (with `created_by` = admin), increases `WarehouseStock`, and updates `WarehouseItem.last_unit_price` (procurement-related, per §8.6). No `Purchase` record is created.

## 9.7 Weekend Salary Settlement (Admin)

1. Admin views each worker's pending balance: total earned (day-equivalents × `daily_wage`) minus total advances paid.
2. Admin distributes settlement cash to the worker outside the app.
3. Admin marks the worker as paid. A `WorkerPayment` with `payment_type = settlement` is created. No wallet deduction occurs.

---

# 10. Role Responsibilities

## 10.1 Admin

**Account Management** — Create supervisor and driver accounts (with `driver_type` for drivers); activate or deactivate any account; edit user details.

**Worker Management** — Register, edit, activate, or deactivate workers.

**Site Management** — Create and edit construction sites; assign and remove supervisors from sites.

**Warehouse Management** — Add and edit warehouse locations; maintain the global item catalog; record large procurement purchases directly to warehouse (via `StockMovement` IN, §9.6); view current stock levels per warehouse.

**Weekend Salary Settlement** — View pending salary balance per worker; mark workers as paid after cash is distributed; settlement recorded as `WorkerPayment` with `payment_type = settlement`.

**Reporting & Oversight** — View all expenses per site broken down by `expense_type`; view supervisor wallet balance and full transaction history; view attendance across all workers, supervisors, and drivers; view Ajax and Hitachi driver logs and associated site expenses; view Normal driver purchases and bata/vehicle rent costs; view all stock movement history.

## 10.2 Supervisor

**Worker Management** — Register new workers with name and daily wage; edit worker details; activate or deactivate workers.

**Attendance** — Mark attendance for workers (present, absent, or half-day), including split half-days across two sites on the same day; mark own attendance.

**Wallet Management** — Credit own wallet when cash is received from admin; view current wallet balance and full credit/debit history.

**Expense Recording** — Record any site expense against a specific site; each expense auto-debits the supervisor wallet.

**Material Transfers** — Transfer items from warehouse to site; system auto-calculates the transfer expense using `last_unit_price` and creates a `material_transfer` Expense.

**Worker Advances** — Pay daily advances to workers (amount entered manually); each advance debits the supervisor wallet atomically with a `SupervisorBalanceLog` entry.

## 10.3 Ajax Driver

**Daily Log** — Select site and date; enter number of mixes completed; system auto-calculates the expense at `rate_per_mix` and creates an `ajax_service` Expense for the site.

**Attendance** — Mark own attendance (not site-specific).

## 10.4 Hitachi Driver

**Daily Log** — Select site and date; enter hours worked; system auto-calculates the expense at `hourly_rate` and creates a `hitachi_service` Expense for the site.

**Attendance** — Mark own attendance (not site-specific).

## 10.5 Normal Driver

**Purchase Recording** — Record material purchases: item, quantity, unit price, vendor, date; specify destination (site or warehouse) and vehicle type (own, outer, or none); enter `vehicle_rent` — bata is auto-calculated as 30% if `vehicle_type = own`.

**Attendance** — Mark own attendance (not site-specific).

---

# 11. API Contract

## 11.1 Overview

| | |
|---|---|
| Protocol | HTTPS |
| Architecture | REST |
| Data Format | JSON |
| Authentication | JWT Bearer Token |
| API Version | v1 |
| Base URL | /api/v1 |

## 11.2 API Design Principles

Resources are nouns, always plural (`/users`, `/workers`, `/sites`, `/attendance`, `/expenses`). Verbs are avoided (`POST /createWorker` is incorrect; `POST /workers` is correct).

## 11.3 Standard Response Format

**Success**
```json
{
  "success": true,
  "message": "Operation completed successfully.",
  "data": {}
}
```

**Error**
```json
{
  "success": false,
  "message": "Validation failed.",
  "errors": {}
}
```

This is the single, canonical response envelope for all endpoints. Success responses always carry a `data` object; error responses always carry an `errors` object.

## 11.4 Authentication

Protected endpoints require `Authorization: Bearer <JWT_TOKEN>`.

Public endpoints:
- `POST /auth/login`
- `POST /auth/refresh`

## 11.5 HTTP Status Codes

| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Created |
| 204 | Deleted |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 500 | Internal Server Error |

## 11.6 Pagination

All list endpoints support `?page=1&page_size=20`, with optional `search`, `sort`, `order`, and filter parameters. List endpoints must never return unbounded result sets.

## 11.7 Endpoint Index

Status legend: 🟡 Planned · 🟢 Implemented · 🔴 Deprecated

**Authentication**

| Status | Method | Endpoint |
|---|---|---|
| 🟡 | POST | /auth/login |
| 🟡 | POST | /auth/refresh |
| 🟡 | POST | /auth/logout |
| 🟡 | GET | /auth/me |

**Users**

| Status | Method | Endpoint |
|---|---|---|
| 🟡 | POST | /users |
| 🟡 | GET | /users |
| 🟡 | GET | /users/{id} |
| 🟡 | PATCH | /users/{id} |
| 🟡 | DELETE | /users/{id} |

**Sites**

| Status | Method | Endpoint |
|---|---|---|
| 🟡 | POST | /sites |
| 🟡 | GET | /sites |
| 🟡 | GET | /sites/{id} |
| 🟡 | PATCH | /sites/{id} |
| 🟡 | DELETE | /sites/{id} |
| 🟡 | POST | /sites/{site_id}/supervisors |
| 🟡 | GET | /sites/{site_id}/supervisors |
| 🟡 | DELETE | /sites/{site_id}/supervisors/{supervisor_id} |

**Workers**

| Status | Method | Endpoint |
|---|---|---|
| 🟡 | POST | /workers |
| 🟡 | GET | /workers |
| 🟡 | GET | /workers/{id} |
| 🟡 | PATCH | /workers/{id} |
| 🟡 | DELETE | /workers/{id} |

**Attendance**

| Status | Method | Endpoint |
|---|---|---|
| 🟡 | POST | /attendance |
| 🟡 | GET | /attendance |
| 🟡 | PATCH | /attendance/{id} |

**Expenses**

| Status | Method | Endpoint |
|---|---|---|
| 🟡 | POST | /expenses |
| 🟡 | GET | /expenses |
| 🟡 | GET | /expenses/{id} |

**Wallet**

| Status | Method | Endpoint |
|---|---|---|
| 🟡 | POST | /wallet/credit |
| 🟡 | GET | /wallet/balance |
| 🟡 | GET | /wallet/history |

**Warehouse**

| Status | Method | Endpoint |
|---|---|---|
| 🟡 | POST | /warehouses |
| 🟡 | GET | /warehouses |
| 🟡 | PATCH | /warehouses/{id} |

**Warehouse Items**

| Status | Method | Endpoint |
|---|---|---|
| 🟡 | POST | /warehouse-items |
| 🟡 | GET | /warehouse-items |
| 🟡 | PATCH | /warehouse-items/{id} |

**Warehouse Stock**

| Status | Method | Endpoint |
|---|---|---|
| 🟡 | GET | /warehouse-stock |
| 🟡 | GET | /warehouse-stock/{warehouse_id} |

**Stock Movement**

| Status | Method | Endpoint |
|---|---|---|
| 🟡 | POST | /stock-movements |
| 🟡 | GET | /stock-movements |

**Purchases**

| Status | Method | Endpoint |
|---|---|---|
| 🟡 | POST | /purchases |
| 🟡 | GET | /purchases |
| 🟡 | GET | /purchases/{id} |

**Ajax Driver Logs**

| Status | Method | Endpoint |
|---|---|---|
| 🟡 | POST | /ajax-logs |
| 🟡 | GET | /ajax-logs |

**Hitachi Driver Logs**

| Status | Method | Endpoint |
|---|---|---|
| 🟡 | POST | /hitachi-logs |
| 🟡 | GET | /hitachi-logs |

**Worker Payments**

| Status | Method | Endpoint |
|---|---|---|
| 🟡 | POST | /worker-payments |
| 🟡 | GET | /worker-payments |

**Reports**

| Status | Method | Endpoint |
|---|---|---|
| 🟡 | GET | /reports/attendance |
| 🟡 | GET | /reports/expenses |
| 🟡 | GET | /reports/salary |
| 🟡 | GET | /reports/wallet |
| 🟡 | GET | /reports/warehouse |

`/reports/salary` is the sole endpoint for viewing worker salary balances, covering both historical reporting and the admin's pre-settlement pending-balance view.

**Dashboard**

| Status | Method | Endpoint |
|---|---|---|
| 🟡 | GET | /dashboard |

## 11.8 API Documentation Requirements

Every completed endpoint must include: request DTO, response DTO, validation rules, authorization requirements, possible error responses, an example request, and an example response. Whenever an endpoint moves from Planned to Implemented, this documentation must be added and the status updated in this specification.

---

# 12. Folder Structure

```
csms-backend/
│
├── .env.example
├── .gitignore
├── .pre-commit-config.yaml
├── LICENSE
├── README.md
├── requirements.txt
├── alembic.ini
├── Dockerfile
├── docker-compose.yml
│
├── alembic/
│   ├── README
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── business_rules/
│   ├── database/
│   ├── prompts/
│   └── adr/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py
│   │       └── endpoints/
│   │           ├── auth.py
│   │           ├── users.py
│   │           ├── workers.py
│   │           ├── attendance.py
│   │           ├── sites.py
│   │           ├── expenses.py
│   │           ├── warehouse.py
│   │           ├── purchases.py
│   │           ├── ajax_logs.py
│   │           ├── hitachi_logs.py
│   │           ├── reports.py
│   │           └── dashboard.py
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── permissions.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   │
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── database.py
│   │   ├── session.py
│   │   └── init_db.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── worker.py
│   │   ├── attendance.py
│   │   ├── expense.py
│   │   ├── purchase.py
│   │   ├── warehouse.py
│   │   ├── stock.py
│   │   ├── wallet.py
│   │   ├── site.py
│   │   ├── site_supervisor.py
│   │   ├── worker_payment.py
│   │   ├── ajax_driver_log.py
│   │   └── hitachi_driver_log.py
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── worker.py
│   │   ├── attendance.py
│   │   ├── expense.py
│   │   ├── purchase.py
│   │   ├── warehouse.py
│   │   ├── report.py
│   │   ├── dashboard.py
│   │   ├── site_supervisor.py
│   │   ├── worker_payment.py
│   │   ├── ajax_driver_log.py
│   │   └── hitachi_driver_log.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user_repository.py
│   │   ├── worker_repository.py
│   │   ├── attendance_repository.py
│   │   ├── expense_repository.py
│   │   ├── purchase_repository.py
│   │   ├── warehouse_repository.py
│   │   ├── stock_repository.py
│   │   ├── wallet_repository.py
│   │   ├── report_repository.py
│   │   ├── site_supervisor_repository.py
│   │   ├── worker_payment_repository.py
│   │   ├── ajax_log_repository.py
│   │   └── hitachi_log_repository.py
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── worker_service.py
│   │   ├── attendance_service.py
│   │   ├── expense_service.py
│   │   ├── purchase_service.py
│   │   ├── warehouse_service.py
│   │   ├── wallet_service.py
│   │   ├── report_service.py
│   │   ├── dashboard_service.py
│   │   ├── site_supervisor_service.py
│   │   ├── worker_payment_service.py
│   │   ├── salary_service.py
│   │   ├── ajax_log_service.py
│   │   └── hitachi_log_service.py
│   │
│   ├── dependencies/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── roles.py
│   │   ├── pagination.py
│   │   └── permissions.py
│   │
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── logging.py
│   │   ├── request_id.py
│   │   └── timing.py
│   │
│   ├── validators/
│   │   ├── __init__.py
│   │   ├── attendance.py
│   │   ├── expense.py
│   │   ├── purchase.py
│   │   └── worker.py
│   │
│   ├── constants/
│   │   ├── __init__.py
│   │   ├── enums.py
│   │   ├── permissions.py
│   │   └── roles.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── datetime.py
│       ├── helpers.py
│       ├── pagination.py
│       └── response.py
│
├── scripts/
│   ├── seed_admin.py
│   └── seed_demo_data.py
│
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── fixtures/
    ├── factories/
    ├── api/
    ├── repositories/
    ├── services/
    ├── integration/
    └── test_health.py
```

No folder should be added beyond what is listed here without an explicit, documented revision to this specification.

---

# 13. Coding Standards

**Naming conventions**

| Context | Convention |
|---|---|
| Python variables and functions | snake_case |
| Python classes | PascalCase |
| Python constants | UPPER_CASE |
| Database columns | snake_case |
| Database table names | As defined in §6 (e.g. `Site`, `Workers`, `Attendance`) — used exactly as specified, not force-pluralized |

Every function must have type hints. Every public method should have a docstring. Functions are kept focused on a single responsibility, with no duplicated logic. Readable code is preferred over clever code.

**SQLAlchemy**

- SQLAlchemy 2.0 typed-ORM style throughout.
- Relationships declared explicitly; lazy loading used only where appropriate.
- Raw SQL avoided unless strictly necessary; no duplicated queries.
- Eager loading used only where it demonstrably avoids N+1 query patterns.

---

# 14. Error Handling & Logging

**Error Handling**

Business errors use custom exceptions (e.g. `WorkerNotFoundException`, `InsufficientWalletBalanceException`, `AttendanceAlreadyExistsException`, `UnauthorizedDriverException`). `HTTPException` is never raised inside the Service layer — only the API layer converts business exceptions into HTTP responses. Internal implementation details are never exposed through API responses.

**Logging**

Log: authentication failures, transaction failures, unexpected exceptions, critical business events.

Never log: passwords, JWT tokens, sensitive user data.

**Soft Delete**

`Users` and `Workers` use `is_active` as a soft-delete flag; deleted records remain queryable for historical reports. `Site` uses its `status` enum (`active`, `completed`, `on_hold`) as its lifecycle mechanism rather than a boolean flag.

---

# 15. Testing Requirements

Every completed feature must include unit tests, repository tests, and API tests. Business-critical workflows — all atomic transactions listed in §3.3 and §8.7, and the salary day-equivalent cap in §8.5 — must additionally include dedicated transaction tests covering both the success path and rollback-on-failure path.

---

# 16. Non-Goals and Deferred Items

The following are explicitly not part of this specification and must not be implemented without a documented revision to this document:

- Supervisor attendance verification, approval, or rejection, in any form
- A structured `reference_type`/`reference_id` link on `SupervisorBalanceLog`
- A dedicated pending-salary endpoint separate from `/reports/salary`
- A `movement_reason`/`source_type` (or equivalent) field on `StockMovement`
- Any relaxation of the rule that `Purchase.purchased_by` must be `driver_type = normal`
- Role-based authorization restrictions on `POST /stock-movements` — this remains an open item

*End of Specification*
