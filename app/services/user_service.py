"""Service layer placeholders — update user_service to clean placeholder."""

from sqlalchemy.orm import Session


class UserService:
    """Service for User business operations.

    Placeholder — implementation pending Phase 1.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # TODO: Implement user service methods.
