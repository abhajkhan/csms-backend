"""Structured logging configuration for CSMS backend.

Call ``configure_logging()`` once at application startup (in ``main.py``).
Use ``get_logger(__name__)`` in every module that needs a logger.

The format automatically includes:
    - ISO timestamp
    - Log level (8-char padded)
    - Logger name
    - Request ID (from the current async context, or ``-`` when outside a request)
    - Message

Never log passwords, JWT tokens, or sensitive personal data.
Per 02_BACKEND_RULES.md §14 Logging.
"""

import logging
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass


# ─── Request-ID filter ───────────────────────────────────────────────────────


class _RequestIDFilter(logging.Filter):
    """Injects ``request_id`` into every log record.

    Reads from ``REQUEST_ID_CTX_VAR`` set by ``RequestIDMiddleware``.
    Returns ``"-"`` when called outside of an active HTTP request.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        # Late import avoids a startup-time circular import between
        # core.logging and middleware.request_id.
        from app.middleware.request_id import get_request_id  # noqa: PLC0415

        record.request_id = get_request_id() or "-"
        return True


# ─── Public API ──────────────────────────────────────────────────────────────

_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | rid=%(request_id)s | %(message)s"
)
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"


def configure_logging(level: int = logging.INFO) -> None:
    """Configure application-wide structured logging.

    Must be called **once** before the FastAPI application is created.
    Subsequent calls are idempotent because the root logger is not
    re-configured if handlers are already attached.

    Args:
        level: Python logging level constant (default: ``logging.INFO``).
               Pass ``logging.DEBUG`` when ``settings.DEBUG = True``.
    """
    root = logging.getLogger()

    # Guard against double-configuration (e.g. during pytest collection).
    if root.handlers:
        root.setLevel(level)
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT))
    handler.addFilter(_RequestIDFilter())

    root.setLevel(level)
    root.addHandler(handler)

    # Quiet down noisy third-party loggers.
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger that inherits the root configuration.

    Args:
        name: Logger name — always pass ``__name__`` from the calling module.

    Returns:
        A configured ``logging.Logger`` instance.

    Example::

        logger = get_logger(__name__)
        logger.info("Worker %d registered.", worker_id)
    """
    return logging.getLogger(name)
