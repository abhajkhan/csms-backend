"""Warehouse ORM models — placeholder.

Implementation pending Phase 6 — Warehouse & Inventory Management.

Tables:
    warehouses       (§4.11)
    warehouse_items  (§4.12)

Design reference: Construction_System_Design_v2.md §4.11, §4.12

``warehouses`` columns:
    warehouse_id int PK
    name         varchar
    location     varchar

``warehouse_items`` columns:
    item_id         int PK
    name            varchar
    description     text | NULL
    category        enum(cement, metal, sand, aggregate, wood, other)
    unit            varchar(kg, tonne, bag, cubic_meter, piece)
    last_unit_price decimal
"""
