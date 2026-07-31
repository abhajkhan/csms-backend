"""AjaxLogService for Ajax driver logs and automatic expense logging.

Per CSMS_SPEC.md §6.9, §8.4, §9.3 & §12
"""

from sqlalchemy.ext.asyncio import AsyncSession


class AjaxLogService:
    """Service for managing Ajax driver logs."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
