"""Worker ORM model — placeholder.

Implementation pending Phase 2 — Worker Management.

Table: ``workers``
Design reference: Construction_System_Design_v2.md §4.4

Columns to implement:
    worker_id  int PK
    full_name  varchar
    daily_wage decimal
    is_active  boolean
    created_by int FK → users.user_id (admin or supervisor)
"""
