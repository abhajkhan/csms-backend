"""SQLAlchemy declarative base.

All ORM models must inherit from ``Base``.  This module must NOT import any
model modules — model imports belong in ``app/db/init_db.py`` so that Alembic
can discover them without circular imports.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for every SQLAlchemy ORM model."""
