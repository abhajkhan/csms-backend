"""ReportService — placeholder.

Implementation pending Phase 7 — Reporting.
"""

from sqlalchemy.orm import Session


class ReportService:
    """Service for generating read-only reports."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # TODO: Implement report service methods.
