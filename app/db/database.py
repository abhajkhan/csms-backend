"""SQLAlchemy engine factory.

The engine is the single entry-point for all database connectivity.
Session management lives in ``app.db.session``.
"""

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import get_settings

settings = get_settings()

engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,   # verifies connection health before use
    echo=settings.DEBUG,  # logs SQL statements when DEBUG=True
)

