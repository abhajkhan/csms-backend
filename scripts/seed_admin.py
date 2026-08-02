"""Admin seeding script for first-run setup.

Usage::

    python scripts/seed_admin.py

Idempotence:
    Checks if an Admin account or the target phone already exists. If found,
    exits cleanly without creating duplicate records.
"""

from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

# Ensure project root is in sys.path when script is executed directly
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Set Windows asyncio event loop policy for psycopg 3 compatibility
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from sqlalchemy import select

from app.constants.enums import UserRole
from app.core.security import hash_password
from app.db.database import engine
from app.db.session import SessionLocal
from app.models.user import User
from app.repositories.user_repository import UserRepository


async def seed_admin() -> None:
    """Create initial Admin account if none exists."""
    admin_phone = os.getenv("SEED_ADMIN_PHONE", "03000000000").strip()
    admin_password = os.getenv("SEED_ADMIN_PASSWORD", "Admin@123456")

    async with SessionLocal() as session:
        try:
            user_repo = UserRepository(session)

            # Check if user with target phone already exists
            existing_phone = await user_repo.get_by_phone(admin_phone)
            if existing_phone:
                print(
                    f"[INFO] Account with phone '{admin_phone}' already exists. Skipping seeding."
                )
                return

            # Check if any Admin account exists
            stmt = select(User).where(User.role == UserRole.ADMIN.value)
            result = await session.execute(stmt)
            if result.scalar_one_or_none():
                print(
                    "[INFO] An Admin account already exists in the database. Skipping seeding."
                )
                return

            password_hash = hash_password(admin_password)
            admin_user = User(
                role=UserRole.ADMIN.value,
                driver_type=None,
                full_name="Admin",
                phone=admin_phone,
                password_hash=password_hash,
                is_active=True,
                acc_balance=None,
            )

            await user_repo.create(admin_user)
            await session.commit()
            print(f"[SUCCESS] Admin account '{admin_phone}' created successfully.")
        except Exception as e:
            await session.rollback()
            print(f"[ERROR] Failed to seed Admin account: {e}")
            sys.exit(1)
        finally:
            await engine.dispose()


def main() -> None:
    """Entry point for python scripts/seed_admin.py."""
    asyncio.run(seed_admin())


if __name__ == "__main__":
    main()
