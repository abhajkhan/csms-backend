"""Pagination utilities for CSMS backend.

Provides:
    ``PaginationParams`` — dataclass holding ``page`` and ``page_size``.
    ``PaginatedResult``  — typed dataclass wrapping a result page.
    ``paginate()``       — executes a SQLAlchemy 2.0 ``Select`` with paging.
    ``paginate_list()``  — convenience helper for in-memory list slicing.

Per 02_BACKEND_RULES.md §13 Pagination.

Design:
    - Default page size: 20.
    - Maximum page size: 100 (enforced at the dependency layer).
    - Page numbering is 1-indexed (page=1 returns the first page).
    - Both SQLAlchemy 2.0 ``select()`` statements and plain Python lists
      are supported.

Usage::

    # In a route handler:
    from app.dependencies.pagination import get_pagination
    from app.utils.pagination import paginate

    @router.get("/workers")
    def list_workers(
        params: PaginationParams = Depends(get_pagination),
        db: Session = Depends(get_db),
    ):
        stmt = select(Worker).order_by(Worker.worker_id)
        result = paginate(db, stmt, params)
        return paginated_response(result, WorkerResponse)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

T = TypeVar("T")
S = TypeVar("S")

# ─── Defaults ────────────────────────────────────────────────────────────────

DEFAULT_PAGE: int = 1
DEFAULT_PAGE_SIZE: int = 20
MAX_PAGE_SIZE: int = 100


# ─── Data structures ─────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PaginationParams:
    """Immutable pagination input parsed from query parameters.

    Attributes:
        page:      Current page (1-indexed). Must be ≥ 1.
        page_size: Number of items per page. Must be between 1 and 100.
    """

    page: int = DEFAULT_PAGE
    page_size: int = DEFAULT_PAGE_SIZE

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError(f"page must be ≥ 1, got {self.page}.")
        if not 1 <= self.page_size <= MAX_PAGE_SIZE:
            raise ValueError(
                f"page_size must be between 1 and {MAX_PAGE_SIZE}, "
                f"got {self.page_size}."
            )

    @property
    def offset(self) -> int:
        """SQL OFFSET value for the current page."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """SQL LIMIT value (alias for ``page_size``)."""
        return self.page_size


@dataclass
class PaginatedResult(Generic[T]):
    """A single page of query results with metadata.

    Attributes:
        items:       The result items for the current page.
        total:       Total count of matching records (all pages).
        page:        Current page number (1-indexed).
        page_size:   Number of items requested per page.
    """

    items: list[T]
    total: int
    page: int
    page_size: int

    @property
    def total_pages(self) -> int:
        """Total number of pages for the given ``total`` and ``page_size``."""
        if self.page_size <= 0:
            return 0
        return math.ceil(self.total / self.page_size)

    @property
    def has_next(self) -> bool:
        """``True`` when there is at least one more page after the current."""
        return self.page < self.total_pages

    @property
    def has_previous(self) -> bool:
        """``True`` when the current page is not the first page."""
        return self.page > 1

    def map(self, fn: Callable[[T], S]) -> PaginatedResult[S]:
        """Return a new ``PaginatedResult`` with items transformed by *fn*.

        Useful for converting ORM model instances to response DTOs::

            result = paginate(db, stmt, params)
            dto_result = result.map(WorkerResponse.model_validate)

        Args:
            fn: A callable that transforms each item.

        Returns:
            A new ``PaginatedResult`` containing the transformed items.
        """
        return PaginatedResult(
            items=[fn(item) for item in self.items],
            total=self.total,
            page=self.page,
            page_size=self.page_size,
        )

    def to_meta_dict(self) -> dict[str, int]:
        """Return pagination metadata as a plain dictionary.

        Suitable for direct use in JSON response bodies.

        Returns:
            ``{"page": ..., "page_size": ..., "total": ..., "total_pages": ...}``
        """
        return {
            "page": self.page,
            "page_size": self.page_size,
            "total": self.total,
            "total_pages": self.total_pages,
        }


# ─── SQLAlchemy 2.0 paginator ─────────────────────────────────────────────────


def paginate(
    db: Session,
    stmt: Select[Any],
    params: PaginationParams,
) -> PaginatedResult[Any]:
    """Execute a paginated SQLAlchemy 2.0 select statement.

    Runs two queries:
        1. A ``COUNT(*)`` over the full result set.
        2. The original statement with ``OFFSET`` and ``LIMIT`` applied.

    The count query wraps *stmt* as a subquery to avoid duplicating
    ``JOIN`` / ``WHERE`` clauses.

    Args:
        db:     An active SQLAlchemy ``Session``.
        stmt:   A ``select()`` statement **without** offset/limit applied.
        params: Pagination parameters.

    Returns:
        A ``PaginatedResult`` containing the fetched items and metadata.

    Example::

        stmt = select(Worker).where(Worker.is_active.is_(True))
        result = paginate(db, stmt, params)
    """
    # Total count — wrap original statement as a subquery.
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total: int = db.execute(count_stmt).scalar_one()

    if total == 0:
        return PaginatedResult(
            items=[], total=0, page=params.page, page_size=params.page_size
        )

    # Paginated fetch.
    paginated_stmt = stmt.offset(params.offset).limit(params.limit)
    items: list[Any] = list(db.execute(paginated_stmt).scalars().all())

    return PaginatedResult(
        items=items,
        total=total,
        page=params.page,
        page_size=params.page_size,
    )


# ─── In-memory list paginator ─────────────────────────────────────────────────


def paginate_list(
    items: list[T],
    params: PaginationParams,
) -> PaginatedResult[T]:
    """Slice a pre-loaded list according to pagination parameters.

    Useful when the full list is already available in memory (e.g. from a
    cached result or a small fixed dataset).

    Args:
        items:  The complete list of items.
        params: Pagination parameters.

    Returns:
        A ``PaginatedResult`` with the appropriate slice.
    """
    total = len(items)
    start = params.offset
    end = start + params.page_size
    page_items = items[start:end]

    return PaginatedResult(
        items=page_items,
        total=total,
        page=params.page,
        page_size=params.page_size,
    )
