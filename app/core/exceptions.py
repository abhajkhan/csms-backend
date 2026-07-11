"""Custom exception hierarchy for CSMS backend.

Design principles:
    - Services raise **domain exceptions** (never ``HTTPException``).
    - The API layer converts domain exceptions to HTTP responses via handlers
      registered by ``register_exception_handlers(app)``.
    - Each exception carries a ``message`` attribute for the response body.

Per 02_BACKEND_RULES.md §11 Error Handling.

Usage::

    # In a service:
    raise WorkerNotFoundException(worker_id=42)

    # In main.py (once):
    from app.core.exceptions import register_exception_handlers
    register_exception_handlers(app)
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


# ─── Base ────────────────────────────────────────────────────────────────────


class CSMSBaseException(Exception):
    """Root exception for all CSMS business errors.

    Args:
        message: Human-readable error description returned in the API response.
    """

    http_status: int = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message: str = "An unexpected error occurred.") -> None:
        super().__init__(message)
        self.message = message


# ─── Not Found (404) ─────────────────────────────────────────────────────────


class NotFoundException(CSMSBaseException):
    """Raised when a requested resource does not exist."""

    http_status: int = status.HTTP_404_NOT_FOUND


class UserNotFoundException(NotFoundException):
    """Raised when a user record cannot be located by its primary key."""

    def __init__(self, user_id: int) -> None:
        super().__init__(f"User with id={user_id} was not found.")


class WorkerNotFoundException(NotFoundException):
    """Raised when a worker record cannot be located by its primary key."""

    def __init__(self, worker_id: int) -> None:
        super().__init__(f"Worker with id={worker_id} was not found.")


class SiteNotFoundException(NotFoundException):
    """Raised when a construction site cannot be located by its primary key."""

    def __init__(self, site_id: int) -> None:
        super().__init__(f"Site with id={site_id} was not found.")


class ExpenseNotFoundException(NotFoundException):
    """Raised when an expense record cannot be located."""

    def __init__(self, expense_id: int) -> None:
        super().__init__(f"Expense with id={expense_id} was not found.")


class AttendanceNotFoundException(NotFoundException):
    """Raised when an attendance record cannot be located."""

    def __init__(self, attendance_id: int) -> None:
        super().__init__(
            f"Attendance record with id={attendance_id} was not found."
        )


class PurchaseNotFoundException(NotFoundException):
    """Raised when a purchase record cannot be located."""

    def __init__(self, purchase_id: int) -> None:
        super().__init__(f"Purchase with id={purchase_id} was not found.")


class WarehouseNotFoundException(NotFoundException):
    """Raised when a warehouse record cannot be located."""

    def __init__(self, warehouse_id: int) -> None:
        super().__init__(
            f"Warehouse with id={warehouse_id} was not found."
        )


class ItemNotFoundException(NotFoundException):
    """Raised when a warehouse item cannot be located."""

    def __init__(self, item_id: int) -> None:
        super().__init__(f"Item with id={item_id} was not found.")


# ─── Conflict (409) ──────────────────────────────────────────────────────────


class ConflictException(CSMSBaseException):
    """Raised when a uniqueness constraint or duplicate-data rule is violated."""

    http_status: int = status.HTTP_409_CONFLICT


class AttendanceAlreadyExistsException(ConflictException):
    """Raised when attendance for a labour + site + date combination exists."""

    def __init__(self, labour_id: int, date: str) -> None:
        super().__init__(
            f"Attendance for labour id={labour_id} on {date} already exists."
        )


class PhoneAlreadyRegisteredException(ConflictException):
    """Raised when a phone number is already associated with another account."""

    def __init__(self, phone: str) -> None:
        super().__init__(f"Phone number {phone} is already registered.")


# ─── Unauthorized / Authentication (401) ─────────────────────────────────────


class AuthenticationException(CSMSBaseException):
    """Raised when credentials are missing or invalid."""

    http_status: int = status.HTTP_401_UNAUTHORIZED


class InvalidCredentialsException(AuthenticationException):
    """Raised when the phone/password combination does not match."""

    def __init__(self) -> None:
        super().__init__("Invalid phone number or password.")


class TokenExpiredException(AuthenticationException):
    """Raised when a JWT has passed its expiry time."""

    def __init__(self) -> None:
        super().__init__("Authentication token has expired.")


class InvalidTokenException(AuthenticationException):
    """Raised when a JWT cannot be decoded or is structurally invalid."""

    def __init__(self) -> None:
        super().__init__("Authentication token is invalid.")


# ─── Authorization / Forbidden (403) ─────────────────────────────────────────


class AuthorizationException(CSMSBaseException):
    """Raised when the authenticated user lacks permission for an action."""

    http_status: int = status.HTTP_403_FORBIDDEN

    def __init__(
        self, message: str = "You do not have permission to perform this action."
    ) -> None:
        super().__init__(message)


class InsufficientRoleException(AuthorizationException):
    """Raised when a user's role does not meet the minimum required role."""

    def __init__(self, required_roles: list[str]) -> None:
        readable = ", ".join(required_roles)
        super().__init__(
            f"This action requires one of the following roles: {readable}."
        )


class UnauthorizedDriverException(AuthorizationException):
    """Raised when a driver attempts an operation not allowed for their type."""

    def __init__(self, required_type: str) -> None:
        super().__init__(
            f"This action is restricted to {required_type} drivers."
        )


class InactiveUserException(AuthorizationException):
    """Raised when a deactivated user attempts to authenticate."""

    def __init__(self) -> None:
        super().__init__(
            "Your account is deactivated. Contact the administrator."
        )


# ─── Business Rule Violations (422) ──────────────────────────────────────────


class BusinessRuleException(CSMSBaseException):
    """Raised when a domain business rule is violated.

    These errors are semantically valid requests (correct shape) but break
    a rule defined in the system design.
    """

    http_status: int = status.HTTP_422_UNPROCESSABLE_ENTITY


class InsufficientWalletBalanceException(BusinessRuleException):
    """Raised when a supervisor's wallet lacks funds for an operation."""

    def __init__(self, available: float, required: float) -> None:
        super().__init__(
            f"Insufficient wallet balance. "
            f"Available: {available:.2f}, required: {required:.2f}."
        )


class SiteNotActiveException(BusinessRuleException):
    """Raised when an operation is attempted on an inactive site."""

    def __init__(self, site_id: int) -> None:
        super().__init__(
            f"Site id={site_id} is not active and cannot accept new records."
        )


class WorkerNotActiveException(BusinessRuleException):
    """Raised when an operation is attempted on a deactivated worker."""

    def __init__(self, worker_id: int) -> None:
        super().__init__(
            f"Worker id={worker_id} is deactivated."
        )


class InvalidDriverTypeForActionException(BusinessRuleException):
    """Raised when a driver type is not valid for the requested action."""

    def __init__(self, action: str, allowed_types: list[str]) -> None:
        readable = ", ".join(allowed_types)
        super().__init__(
            f"Action '{action}' is only available to: {readable} drivers."
        )


class AttendanceNotVerifiedException(BusinessRuleException):
    """Raised when an operation requires verified supervisor attendance."""

    def __init__(self, date: str) -> None:
        super().__init__(
            f"Supervisor attendance for {date} has not been verified by admin."
        )


# ─── Handler registration ────────────────────────────────────────────────────


def register_exception_handlers(app: FastAPI) -> None:
    """Register all CSMS exception handlers on the FastAPI application.

    Must be called **after** ``FastAPI()`` is instantiated and **before**
    the application starts accepting requests.

    Handles:
        - All ``CSMSBaseException`` subclasses → appropriate HTTP status.
        - ``RequestValidationError`` → 422 with field-level detail.
        - ``SQLAlchemyError`` → 500 (logged, detail hidden from clients).
        - Unhandled ``Exception`` → 500 (logged, detail hidden from clients).

    Args:
        app: The FastAPI application instance.
    """
    from app.utils.response import error_response  # avoid top-level circularity

    # ── CSMS domain exceptions ───────────────────────────────────────────────

    @app.exception_handler(NotFoundException)
    async def _not_found(
        request: Request, exc: NotFoundException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_response(exc.message),
        )

    @app.exception_handler(ConflictException)
    async def _conflict(
        request: Request, exc: ConflictException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=error_response(exc.message),
        )

    @app.exception_handler(AuthenticationException)
    async def _unauthenticated(
        request: Request, exc: AuthenticationException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=error_response(exc.message),
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(AuthorizationException)
    async def _forbidden(
        request: Request, exc: AuthorizationException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=error_response(exc.message),
        )

    @app.exception_handler(BusinessRuleException)
    async def _business_rule(
        request: Request, exc: BusinessRuleException
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(exc.message),
        )

    @app.exception_handler(CSMSBaseException)
    async def _base(
        request: Request, exc: CSMSBaseException
    ) -> JSONResponse:
        logger.error("Unhandled CSMS exception: %s", exc.message)
        return JSONResponse(
            status_code=exc.http_status,
            content=error_response(exc.message),
        )

    # ── FastAPI validation errors ────────────────────────────────────────────

    @app.exception_handler(RequestValidationError)
    async def _validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response(
                message="Request validation failed.",
                errors=exc.errors(),
            ),
        )

    # ── Database errors ──────────────────────────────────────────────────────

    @app.exception_handler(SQLAlchemyError)
    async def _db_error(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        rid = getattr(request.state, "request_id", "-")
        logger.exception(
            "Database error on %s %s | rid=%s",
            request.method,
            request.url.path,
            rid,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("A database error occurred."),
        )

    # ── Catch-all ────────────────────────────────────────────────────────────

    @app.exception_handler(Exception)
    async def _unhandled(
        request: Request, exc: Exception
    ) -> JSONResponse:
        rid = getattr(request.state, "request_id", "-")
        logger.exception(
            "Unhandled exception on %s %s | rid=%s",
            request.method,
            request.url.path,
            rid,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response("An internal server error occurred."),
        )
