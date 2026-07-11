"""Standard API response builder utilities.

Produces the canonical JSON envelope defined in:
    02_BACKEND_RULES.md §12 Response Format
    03_API_CONTRACT.md §3 Standard Response Structure

Every API response — success or error — uses one of these builders.
Route handlers must **never** construct ad-hoc response dicts directly.

Usage::

    from app.utils.response import success_response, error_response, paginated_response
    from app.utils.pagination import PaginatedResult

    # Simple success
    return success_response(data=user_dto, message="User retrieved.")

    # Created
    return success_response(  # type: ignore[return-value]
        data=worker_dto, message="Worker registered.", status_code=201
    )

    # Error
    return error_response(message="Site not found.")

    # Paginated list
    return paginated_response(result, schema=WorkerResponse)
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from fastapi.responses import JSONResponse

T = TypeVar("T")


# ─── Success ─────────────────────────────────────────────────────────────────


def success_response(
    data: Any = None,
    message: str = "Operation completed successfully.",
    status_code: int = 200,
) -> JSONResponse:
    """Return a standard success response as a FastAPI ``JSONResponse``.

    Args:
        data:        The response payload (serialisable).  ``None`` when the
                     operation returns no body (e.g. a DELETE).
        message:     Human-readable description of the outcome.
        status_code: HTTP status code (default: 200).

    Returns:
        ``{"success": True, "message": ..., "data": ...}``

    Example::

        return success_response(data=dto, message="Worker registered.", status_code=201)
    """
    return JSONResponse(
        status_code=status_code,
        content=_success_dict(data=data, message=message),
    )


def _success_dict(
    data: Any = None,
    message: str = "Operation completed successfully.",
) -> dict[str, Any]:
    """Return the raw success envelope dict (used by exception handlers)."""
    return {"success": True, "message": message, "data": data}


# ─── Error ───────────────────────────────────────────────────────────────────


def error_response(
    message: str,
    errors: Any = None,
    status_code: int = 400,
) -> dict[str, Any]:
    """Return the raw error envelope dict.

    Returned as a plain ``dict`` (not a ``JSONResponse``) so it can be used
    both inside ``@app.exception_handler`` callbacks (which expect a dict
    for ``JSONResponse(content=...)``) and directly in routes.

    Args:
        message:     Human-readable error description.
        errors:      Optional structured error details (e.g. Pydantic field errors).
        status_code: Not used here — the caller wraps this in a JSONResponse.

    Returns:
        ``{"success": False, "message": ..., "errors": ...}``
    """
    return {"success": False, "message": message, "errors": errors}


# ─── Paginated ───────────────────────────────────────────────────────────────


def paginated_response(
    result: Any,  # PaginatedResult[T]
    schema: Callable[..., Any] | None = None,
    message: str = "OK",
    status_code: int = 200,
) -> JSONResponse:
    """Return a standard paginated list response.

    Args:
        result:      A ``PaginatedResult`` returned by ``paginate()`` or
                     ``paginate_list()``.
        schema:      Optional Pydantic model class.  When provided, each item
                     is serialised via ``schema.model_validate(item).model_dump()``.
        message:     Human-readable description (default: ``"OK"``).
        status_code: HTTP status code (default: 200).

    Returns:
        ``{"success": True, "message": ..., "data": [...], "meta": {...}}``

    Example::

        result = paginate(db, stmt, params)
        return paginated_response(result, schema=WorkerResponse)
    """
    if schema is not None:
        items = [schema.model_validate(item).model_dump() for item in result.items]
    else:
        items = result.items

    content = {
        "success": True,
        "message": message,
        "data": items,
        "meta": result.to_meta_dict(),
    }

    return JSONResponse(status_code=status_code, content=content)


# ─── No-content ──────────────────────────────────────────────────────────────


def no_content_response() -> JSONResponse:
    """Return a 204 No Content response (e.g. for successful DELETE).

    Returns:
        An empty ``JSONResponse`` with status 204.
    """
    return JSONResponse(status_code=204, content=None)
