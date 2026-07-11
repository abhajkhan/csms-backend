"""User ORM model — placeholder.

Implementation pending Phase 1 — Auth & User Management.

Table: ``users``
Design reference: Construction_System_Design_v2.md §4.1

Columns to implement:
    user_id       int PK
    role          enum(admin, supervisor, driver)
    driver_type   enum(hitachi, ajax, normal) | NULL
    full_name     varchar
    phone         varchar UNIQUE
    password_hash varchar
    is_active     boolean
    acc_balance   decimal | NULL  (supervisors only)
"""
