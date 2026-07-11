"""Purchase ORM model — placeholder.

Implementation pending Phase 5 — Normal Driver Purchase Management.

Table: ``purchases``
Design reference: Construction_System_Design_v2.md §4.15

Columns to implement:
    purchase_id      int PK
    purchased_by     int FK → users.user_id  (must be driver_type=normal)
    item_id          int FK → warehouse_items.item_id
    site_id          int FK → sites.site_id | NULL  (when destination=warehouse)
    warehouse_id     int FK → warehouses.warehouse_id | NULL  (when dest=site)
    destination_type enum(site, warehouse)
    quantity         decimal
    unit_price       decimal
    total_amount     decimal
    unit             varchar
    purchased_from   varchar
    vehicle_type     enum(own, outer, none)
    vehicle_rent     decimal
    purchase_date    datetime
    note             text | NULL

Auto-creates Expense entries: driver_material, driver_bata (own vehicle),
driver_vehicle_rent (outer vehicle).
"""
