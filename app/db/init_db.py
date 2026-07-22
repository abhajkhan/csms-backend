"""Database initialisation — model registry.

Imports every ORM model module so that ``Base.metadata`` is fully populated
before Alembic or ``Base.metadata.create_all()`` is called.

Import this module once at startup (already done in ``alembic/env.py``).
"""

# Import order: User first (many FKs reference it), then outward.
import app.models.user  # noqa: F401
import app.models.site  # noqa: F401
import app.models.worker  # noqa: F401
import app.models.attendance  # noqa: F401
import app.models.wallet  # noqa: F401
import app.models.expense  # noqa: F401
import app.models.warehouse  # noqa: F401
import app.models.stock  # noqa: F401
import app.models.purchase  # noqa: F401
