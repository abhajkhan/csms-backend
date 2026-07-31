"""Pytest configuration and shared async fixtures.

Provides:
    ``client``       — AsyncClient for testing API endpoints.
    ``db_session``   — AsyncSession for unit tests that need DB access.
"""

from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

_SQLITE_URL = "sqlite+aiosqlite:///:memory:"

_test_engine = create_async_engine(
    _SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

_TestingSessionLocal = async_sessionmaker(
    bind=_test_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database():
    """Create all tables once for the test session, then drop them."""
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async database session for isolated testing."""
    async with _TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Return an AsyncClient for testing endpoints."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def db_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Return an AsyncClient with the DB dependency overridden."""
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    del app.dependency_overrides[get_db]
