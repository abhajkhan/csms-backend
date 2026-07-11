"""Shared FastAPI dependencies.

Re-exports commonly used dependencies so endpoints can import from a single
location::

    from app.api.deps import get_db

Per 02_BACKEND_RULES.md §4 Dependency Injection.
"""

from app.db.session import get_db

__all__ = ["get_db"]
