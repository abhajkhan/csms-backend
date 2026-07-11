"""AttendanceService — placeholder.

Implementation pending Phase 3 — Attendance Management.

Critical business rule to implement:
    If admin sets is_verified=False on a supervisor attendance record,
    all Expense records by that supervisor for that date must be deleted
    atomically within the same transaction.
    Per Construction_System_Design_v2.md §4.5.
"""

from sqlalchemy.orm import Session


class AttendanceService:
    """Service for Attendance business operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # TODO: Implement attendance service methods.
