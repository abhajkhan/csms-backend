"""Common Pydantic schemas shared across modules.

Provides:
    ``PaginatedResponse``  — standard paginated list wrapper.
    ``APIResponse``        — standard success response envelope.
    ``APIError``           — standard error response envelope.

Per 02_BACKEND_RULES.md §12 Response Format and §13 Pagination.
"""

from typing import Any, Generic, TypeVar

from pydantic import BaseModel

DataT = TypeVar("DataT")


class APIResponse(BaseModel, Generic[DataT]):
    """Standard success response envelope."""

    success: bool = True
    message: str = "Operation completed successfully."
    data: DataT | None = None


class APIError(BaseModel):
    """Standard error response envelope."""

    success: bool = False
    message: str
    errors: Any | None = None


class PaginationMeta(BaseModel):
    """Pagination metadata included in list responses."""

    page: int
    page_size: int
    total: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Paginated list response wrapper."""

    success: bool = True
    message: str = "OK"
    data: list[DataT]
    meta: PaginationMeta
