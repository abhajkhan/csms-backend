"""HTTP request/response logging middleware.

Logs every incoming request and its corresponding response at ``INFO`` level.
Log lines include the request method, path, status code, and the request ID
injected by ``RequestIDMiddleware``.

Registration order in ``app.main`` (RequestIDMiddleware must run first so
that ``request.state.request_id`` is available)::

    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RequestIDMiddleware)   # processed last-in, first-out

Per 02_BACKEND_RULES.md §14 Logging.
"""

from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.logging import get_logger

logger = get_logger(__name__)

#: Paths that are never logged (health / metrics endpoints generate noise).
_SKIP_PATHS: frozenset[str] = frozenset({"/health", "/", "/metrics"})


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs HTTP requests and responses with request-ID correlation.

    Each request produces two log lines:
        ``→ METHOD /path  rid=<uuid>``  — on arrival.
        ``← STATUS METHOD /path  rid=<uuid>``  — after the response is ready.

    Paths listed in ``_SKIP_PATHS`` are silently skipped to avoid log noise
    from load-balancer health probes.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        path: str = request.url.path

        if path in _SKIP_PATHS:
            return await call_next(request)

        rid: str = getattr(request.state, "request_id", "-")

        logger.info("→ %s %s  rid=%s", request.method, path, rid)

        response: Response = await call_next(request)

        logger.info(
            "← %s %s %s  rid=%s",
            response.status_code,
            request.method,
            path,
            rid,
        )

        return response
