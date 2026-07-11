"""Warehouse endpoints — placeholder.

Implementation pending Phase 6 — Warehouse & Inventory Management.

Planned endpoints (03_API_CONTRACT.md §8):
    POST   /warehouses           — create warehouse
    GET    /warehouses           — list warehouses
    PATCH  /warehouses/{id}      — update warehouse

    POST   /warehouse-items      — add item to catalog
    GET    /warehouse-items      — list catalog items
    PATCH  /warehouse-items/{id} — update item

    GET    /warehouse-stock                    — all stock levels
    GET    /warehouse-stock/{warehouse_id}     — stock for one warehouse

    POST   /stock-movements      — record IN or OUT movement
    GET    /stock-movements      — list movements
"""

from fastapi import APIRouter

router = APIRouter()

# TODO: Implement warehouse management endpoints.
