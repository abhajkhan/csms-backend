"""Structured logging configuration for CSMS backend.

Call ``configure_logging()`` once at application startup (in ``main.py``).
Use ``get_logger(__name__)`` in every module that needs a logger.

Never log passwords, JWT tokens, or sensitive user data.
Per 02_BACKEND_RULES.md §14 Logging.
"""

import logging
import sys


def configure_logging(level: int = logging.INFO) -> None:
    """Configure application-wide structured logging.

    Args:
        level: Logging level (default: ``logging.INFO``).
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        stream=sys.stdout,
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger instance.

    Args:
        name: Logger name, typically ``__name__`` of the calling module.

    Returns:
        A configured ``logging.Logger`` instance.
    """
    return logging.getLogger(name)
