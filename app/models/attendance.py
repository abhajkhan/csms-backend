"""Attendance ORM model — placeholder.

Implementation pending Phase 3 — Attendance Management.

Table: ``attendance``
Design reference: Construction_System_Design_v2.md §4.5

Columns to implement:
    attendance_id int PK
    date          date
    labour_type   enum(USER, WORKER)
    labour_id     int (polymorphic FK)
    site_id       int FK → sites.site_id (nullable for drivers)
    status        enum(present, absent, half_day)
    is_verified   boolean | NULL  (supervisors only; null for workers/drivers)
    verified_by   int FK → users.user_id | NULL
    verified_at   datetime | NULL

Business rule: if admin sets is_verified=False on a supervisor attendance
record, all Expense records by that supervisor for that date must be deleted
atomically.
"""
