"""Wallet ORM models — placeholder.

Implementation pending Phase 4 — Supervisor Wallet & Worker Payments.

Tables:
    supervisor_balance_logs  (§4.6)
    worker_payments          (§4.7)

Design reference: Construction_System_Design_v2.md §4.6, §4.7

``supervisor_balance_logs`` columns:
    log_id        int PK
    supervisor_id int FK → users.user_id
    txn_type      enum(credit, debit)
    amount        decimal
    note          varchar
    created_at    datetime

``worker_payments`` columns:
    payment_id   int PK
    worker_id    int FK → workers.worker_id
    paid_by      int FK → users.user_id  (supervisor=advance, admin=settlement)
    amount       decimal
    payment_type enum(advance, settlement)
    paid_at      datetime
    note         varchar | NULL

Business rule: Every update to ``users.acc_balance`` must produce a
SupervisorBalanceLog entry in the same transaction.
"""
