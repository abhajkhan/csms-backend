"""Site ORM model — placeholder.

Implementation pending Phase 1 — Site Management.

Table: ``sites``
Design reference: Construction_System_Design_v2.md §4.2

Columns to implement:
    site_id    int PK
    site_name  varchar
    location   varchar
    status     enum(active, completed, on_hold)
    created_at datetime
    created_by int FK → users.user_id (admin)

Related: ``site_supervisors`` junction table (§4.3).
"""
