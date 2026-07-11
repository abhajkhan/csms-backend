"""Authentication endpoints — placeholder.

Implementation pending Phase 1 — Auth & User Management.

Planned endpoints (03_API_CONTRACT.md §8):
    POST  /auth/login    — obtain access + refresh tokens
    POST  /auth/refresh  — exchange refresh token for new access token
    POST  /auth/logout   — invalidate session
    GET   /auth/me       — return authenticated user profile
"""

from fastapi import APIRouter

router = APIRouter()

# TODO: Implement auth endpoints.
