"""ReportRepository — placeholder.

Implementation pending Phase 7 — Reporting.
"""

from sqlalchemy.orm import Session

from app.repositories.base import BaseRepository


class ReportRepository(BaseRepository):
    """Repository for read-only reporting queries."""

    def __init__(self, db: Session) -> None:
        super().__init__(db)

    # TODO: Implement report-specific queries.
