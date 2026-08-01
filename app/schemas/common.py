"""Enhanced common Pydantic schemas shared across modules.

Provides the canonical response envelope types used by all API endpoints.
These models are the Pydantic counterparts to the ``app.utils.response``
builder functions.

Per 02_BACKEND_RULES.md §12 Response Format and §13 Pagination.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field, field_validator

DataT = TypeVar("DataT")


# ─── Success envelopes ───────────────────────────────────────────────────────


class StandardResponse(BaseModel):
    """Standard generic response envelope with success flag and message."""

    success: bool = True
    message: str = "Operation completed successfully."


class APIResponse(BaseModel, Generic[DataT]):
    """Standard success response envelope."""

    success: bool = True
    message: str = "Operation completed successfully."
    data: DataT | None = None


# ─── Error envelope ──────────────────────────────────────────────────────────


class APIError(BaseModel):
    """Standard error response envelope."""

    success: bool = False
    message: str
    errors: Any | None = None


# ─── Pagination metadata ─────────────────────────────────────────────────────


class PaginationMeta(BaseModel):
    """Metadata describing a paginated result set."""

    page: int = Field(..., ge=1)
    page_size: int = Field(..., ge=1)
    total: int = Field(..., ge=0)
    total_pages: int = Field(..., ge=0)

    @field_validator("total_pages")
    @classmethod
    def _total_pages_consistent(cls, v: int, info: Any) -> int:
        """Ensure total_pages ≥ 0."""
        return max(v, 0)


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Standard paginated list response envelope."""

    success: bool = True
    message: str = "OK"
    data: list[DataT]
    meta: PaginationMeta


# ─── No-content ──────────────────────────────────────────────────────────────


class NoContentResponse(BaseModel):
    """Schema for successful operations with no return body (e.g. DELETE)."""

    success: bool = True
    message: str = "Resource deleted successfully."
