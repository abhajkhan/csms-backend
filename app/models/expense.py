"""Expense ORM model — placeholder.

Implementation pending Phase 4 — Expense Management.

Table: ``expenses``
Design reference: Construction_System_Design_v2.md §4.8

Columns to implement:
    expense_id     int PK
    date           date
    recorded_at    datetime
    amount         decimal
    site_id        int FK → sites.site_id
    recorded_by    int FK → users.user_id
    expense_type   enum(material_transfer, cash_purchase, driver_material,
                        driver_bata, driver_vehicle_rent, ajax_service,
                        hitachi_service, misc)
    reference_id   int | NULL
    reference_type enum(stock_movement, purchase, ajax_log, hitachi_log) | NULL
    description    text

Auto-created by: AjaxDriverLog, HitachiDriverLog, StockMovement OUT, Purchase.
"""
