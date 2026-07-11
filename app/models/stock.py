"""Stock ORM models — placeholder.

Implementation pending Phase 6 — Warehouse & Inventory Management.

Tables:
    warehouse_stock    (§4.13)
    stock_movements    (§4.14)
    ajax_driver_logs   (§4.9)
    hitachi_driver_logs (§4.10)

Design reference: Construction_System_Design_v2.md §4.13, §4.14, §4.9, §4.10

``warehouse_stock`` columns:
    stock_id     int PK
    warehouse_id int FK → warehouses
    item_id      int FK → warehouse_items
    quantity     decimal
    last_updated datetime

``stock_movements`` columns:
    movement_id   int PK
    warehouse_id  int FK
    item_id       int FK
    movement_type enum(IN, OUT)
    quantity      decimal
    unit_price    decimal (snapshot)
    total_amount  decimal
    movement_date datetime
    site_id       int FK | NULL (OUT only)
    reference     varchar
    created_by    int FK

``ajax_driver_logs`` columns:
    log_id       int PK
    driver_id    int FK (driver_type=ajax)
    site_id      int FK
    date         date
    num_mixes    int
    rate_per_mix decimal (snapshot)
    total_amount decimal
    expense_id   int FK → expenses
    note         varchar | NULL

``hitachi_driver_logs`` columns:
    log_id       int PK
    driver_id    int FK (driver_type=hitachi)
    site_id      int FK
    date         date
    hours_worked decimal
    hourly_rate  decimal (snapshot)
    total_amount decimal
    expense_id   int FK → expenses
    note         varchar | NULL
"""
