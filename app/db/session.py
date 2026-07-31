"""Database session factory and FastAPI dependency.

Provides:
    ``SessionLocal`` — configured session factory.
    ``get_db``       — FastAPI dependency that yields a scoped session per request.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.database import engine

SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session, closing it on completion or error.

    Usage::

        @router.get("/example")
        async def example(db: AsyncSession = Depends(get_db)):
            ...
    """
    async with SessionLocal() as session:
        yield session

