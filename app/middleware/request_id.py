"""Request ID middleware.

Attaches a UUID to every incoming request so that all log lines for a single
HTTP request share the same identifier, making distributed tracing trivial.

Provides:
    ``RequestIDMiddleware`` — ASGI middleware class.
    ``get_request_id()``    — returns the ID for the current async context.
    ``REQUEST_ID_CTX_VAR``  — the raw ContextVar (useful for log filters).

Registration in ``app.main``::

    from app.middleware.request_id import RequestIDMiddleware
    app.add_middleware(RequestIDMiddleware)

Usage in a route handler or service::

    from app.middleware.request_id import get_request_id
    rid = get_request_id()   # "7f3a9b2c-…"
"""

import uuid
from contextvars import ContextVar
from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

#: Context variable that holds the request ID for the current async context.
#: Defaults to an empty string when accessed outside of an active request.
REQUEST_ID_CTX_VAR: ContextVar[str] = ContextVar("request_id", default="")

#: Response header name.
_HEADER = "X-Request-ID"


def get_request_id() -> str:
    """Return the request ID bound to the current async context.

    Returns:
        A UUID string for the current request, or ``""`` if called outside
        of an active request context.
    """
    return REQUEST_ID_CTX_VAR.get()


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Generates a UUID per request and propagates it through the stack.

    Sets:
        - ``request.state.request_id`` (available in route handlers via Depends).
        - ``REQUEST_ID_CTX_VAR`` context variable (available in log filters).
        - ``X-Request-ID`` response header (echoed back to the client).

    If the client sends an ``X-Request-ID`` header, that value is used instead
    of generating a new one.  This lets upstream gateways inject their own IDs.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        # Honour a client-supplied ID (gateway / load balancer propagation).
        request_id: str = (
            request.headers.get(_HEADER) or str(uuid.uuid4())
        )

        # Propagate through context variable (sync + async safe).
        token = REQUEST_ID_CTX_VAR.set(request_id)
        request.state.request_id = request_id

        response: Response = await call_next(request)
        response.headers[_HEADER] = request_id

        # Restore the previous context variable state.
        REQUEST_ID_CTX_VAR.reset(token)

        return response
