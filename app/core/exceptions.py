"""Custom exception hierarchy for CSMS backend.

Business exceptions are raised in the Service Layer and converted to HTTP
responses only in the API Layer.  Services must never raise ``HTTPException``.
Per 02_BACKEND_RULES.md §11 Error Handling.

Usage::

    raise WorkerNotFoundException(worker_id=42)
"""


class CSMSBaseException(Exception):
    """Root exception for all CSMS business errors."""

    def __init__(self, message: str = "An unexpected error occurred.") -> None:
        super().__init__(message)
        self.message = message


# ─── Not Found ──────────────────────────────────────────────────────────────


class NotFoundException(CSMSBaseException):
    """Raised when a requested resource does not exist."""


class UserNotFoundException(NotFoundException):
    """Raised when a user cannot be found."""

    def __init__(self, user_id: int) -> None:
        super().__init__(f"User with id={user_id} was not found.")


class WorkerNotFoundException(NotFoundException):
    """Raised when a worker cannot be found."""

    def __init__(self, worker_id: int) -> None:
        super().__init__(f"Worker with id={worker_id} was not found.")


class SiteNotFoundException(NotFoundException):
    """Raised when a construction site cannot be found."""

    def __init__(self, site_id: int) -> None:
        super().__init__(f"Site with id={site_id} was not found.")


# ─── Conflict / Validation ───────────────────────────────────────────────────


class ConflictException(CSMSBaseException):
    """Raised on duplicate or conflicting data."""


class AttendanceAlreadyExistsException(ConflictException):
    """Raised when attendance for a labour on a given date already exists."""


# ─── Authorization ───────────────────────────────────────────────────────────


class AuthorizationException(CSMSBaseException):
    """Raised when an action is not permitted for the current user."""


class UnauthorizedDriverException(AuthorizationException):
    """Raised when a driver attempts an operation not allowed for their type."""


# ─── Business Rule Violations ────────────────────────────────────────────────


class BusinessRuleException(CSMSBaseException):
    """Raised when a core business rule is violated."""


class InsufficientWalletBalanceException(BusinessRuleException):
    """Raised when a supervisor wallet has insufficient funds."""

    def __init__(self, available: float, required: float) -> None:
        super().__init__(
            f"Insufficient wallet balance. "
            f"Available: {available}, required: {required}."
        )
