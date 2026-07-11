"""Database initialisation utilities.

This module is responsible for:
    1. Importing all ORM models so that ``Base.metadata`` is fully populated
       before Alembic or ``create_all`` is called.
    2. Providing any first-run seeding helpers (admin user, lookup data, etc.)

TODO (Phase 1+): import each model module below as they are implemented.
"""

# from app.models import user, site, worker, attendance  # noqa: F401
