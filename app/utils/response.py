"""Standard API response builder utilities.

Provides ``success_response`` and ``error_response`` factories that produce
the canonical JSON envelope defined in 02_BACKEND_RULES.md §12 and
03_API_CONTRACT.md §3.

Usage::

    from app.utils.response import success_response, error_response

    return success_response(data=user, message="User created successfully.")
    return error_response(message="User not found.", errors={"user_id": 42})
"""

from typing import Any


def success_response(
    data: Any = None,
    message: str = "Operation completed successfully.",
) -> dict[str, Any]:
    """Build a standard success response envelope.

    Args:
        data:    Response payload.
        message: Human-readable success message.

    Returns:
        ``{"success": True, "message": ..., "data": ...}``
    """
    return {"success": True, "message": message, "data": data}


def error_response(
    message: str,
    errors: Any = None,
) -> dict[str, Any]:
    """Build a standard error response envelope.

    Args:
        message: Human-readable error description.
        errors:  Optional structured error details.

    Returns:
        ``{"success": False, "message": ..., "errors": ...}``
    """
    return {"success": False, "message": message, "errors": errors}
