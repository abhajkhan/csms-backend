"""app.models package.

All SQLAlchemy ORM models for the CSMS application.

Models are defined in individual modules per entity:
    user.py       — Users table
    site.py       — Sites and SiteSupervisors tables
    worker.py     — Workers table
    attendance.py — Attendance table
    expense.py    — Expenses table
    purchase.py   — Purchases table
    warehouse.py  — Warehouses and WarehouseItems tables
    stock.py      — WarehouseStock, StockMovements, AjaxDriverLogs,
                    HitachiDriverLogs tables
    wallet.py     — SupervisorBalanceLogs and WorkerPayments tables

Import order matters for relationship resolution. Models are imported
in ``app.db.init_db`` to ensure Alembic sees the full metadata.
"""
