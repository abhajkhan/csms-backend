"""Generic base repository — placeholder.

Implementation pending Phase 1.

Planned interface:
    get(id)      → model | None
    get_all()    → list[model]
    create(data) → model
    update(id)   → model
    delete(id)   → None

Per 02_BACKEND_RULES.md §5 Repository Pattern.
"""

from sqlalchemy.orm import Session


class BaseRepository:
    """Abstract base providing common CRUD scaffolding."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # TODO: Implement generic CRUD methods.
