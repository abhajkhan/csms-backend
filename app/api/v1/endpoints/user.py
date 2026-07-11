"""Legacy user endpoint — superseded by users.py.

This file is kept to avoid breaking imports during refactor.
All user management routes now live in ``app.api.v1.endpoints.users``.
"""

from fastapi import APIRouter

router = APIRouter()
