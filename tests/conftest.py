"""Pytest configuration and shared fixtures.

Provides:
    ``client``       — TestClient with a real in-process app (no DB required).
    ``db_session``   — SQLite in-memory session for unit tests that need the DB.

The default ``client`` fixture uses the real FastAPI app without overriding
the database dependency, which is sufficient for testing unauthenticated
endpoints like ``/health`` that do not touch the database.

For tests that require database access, use the ``db_session`` fixture
and override the ``get_db`` dependency via ``app.dependency_overrides``.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app

# ─── In-memory SQLite for isolated unit tests ────────────────────────────────

_SQLITE_URL = "sqlite:///:memory:"

_test_engine = create_engine(
    _SQLITE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=_test_engine,
)


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def db_engine():
    """Create all tables once for the test session, then drop them."""
    Base.metadata.create_all(bind=_test_engine)
    yield _test_engine
    Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture
def db_session(db_engine):
    """Yield a database session wrapped in a rolled-back transaction."""
    connection = db_engine.connect()
    transaction = connection.begin()
    session = _TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client():
    """Return a TestClient for the FastAPI app (no DB override)."""
    return TestClient(app)


@pytest.fixture
def db_client(db_session):
    """Return a TestClient with the DB dependency overridden to use SQLite."""

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield TestClient(app)
    del app.dependency_overrides[get_db]
