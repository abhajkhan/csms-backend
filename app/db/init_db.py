"""Database initialisation — model registry.

Imports all ORM models so that ``Base.metadata`` is fully populated
before Alembic or table creation.
"""

import app.models  # noqa: F401
