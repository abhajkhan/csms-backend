"""Pagination FastAPI dependency.

Parses and validates pagination query parameters from incoming requests.

Usage::

    from app.dependencies.pagination import get_pagination
    from app.utils.pagination import PaginationParams, async_paginate

    @router.get("/workers")
    async def list_workers(
        params: PaginationParams = Depends(get_pagination),
        db: AsyncSession = Depends(get_db),
    ):
        stmt = select(Worker).order_by(Worker.worker_id)
        result = await async_paginate(db, stmt, params)
        return paginated_response(result)

Per 02_BACKEND_RULES.md §14 Pagination.
"""

from fastapi import Query

from app.utils.pagination import (
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    PaginationParams,
)


def get_pagination(
    page: int = Query(
        default=DEFAULT_PAGE,
        ge=1,
        description="Page number (1-indexed).",
    ),
    page_size: int = Query(
        default=DEFAULT_PAGE_SIZE,
        ge=1,
        le=MAX_PAGE_SIZE,
        description=f"Number of items per page (1–{MAX_PAGE_SIZE}).",
    ),
) -> PaginationParams:
    """FastAPI dependency — parse and validate pagination query parameters.

    Args:
        page:      Page number (default: 1, minimum: 1).
        page_size: Items per page (default: 20, range: 1–100).

    Returns:
        A validated, immutable ``PaginationParams`` instance.
    """
    return PaginationParams(page=page, page_size=page_size)
