"""Alembic environment configuration.

Imports:
    - Settings for the live database URL.
    - ``Base`` from ``app.db.base`` (the single source of metadata).
    - All ORM models via ``app.db.init_db`` so metadata is fully populated.

To run migrations::

    alembic upgrade head
    alembic revision --autogenerate -m "describe change"
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# ─── Path setup ──────────────────────────────────────────────────────────────
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# ─── App imports ─────────────────────────────────────────────────────────────
import app.db.init_db  # noqa: F401 — registers all model metadata
from app.core.config import get_settings
from app.db.base import Base

settings = get_settings()
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Override URL from app settings (respects .env file)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations without an active database connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations with a live database connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
