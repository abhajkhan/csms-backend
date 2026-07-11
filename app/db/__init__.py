"""app.db package.

Re-exports the most commonly used database primitives so callers can write::

    from app.db import Base, get_db, engine
"""

from app.db.base import Base
from app.db.database import engine
from app.db.session import SessionLocal, get_db

__all__ = ["Base", "engine", "get_db", "SessionLocal"]
