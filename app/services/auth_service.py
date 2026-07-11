"""AuthService — placeholder.

Implementation pending Phase 1 — Auth & User Management.
"""

from sqlalchemy.orm import Session


class AuthService:
    """Service for authentication and token management."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # TODO: Implement login, refresh, logout, and get_current_user.
