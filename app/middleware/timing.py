"""Request timing middleware.

Measures the wall-clock duration of every HTTP request and exposes it via
the ``X-Process-Time`` response header (value in seconds, 4 decimal places).

Registration in ``app.main``::

    from app.middleware.timing import TimingMiddleware
    app.add_middleware(TimingMiddleware)

The middleware runs **after** ``RequestIDMiddleware`` in the stack so that
``X-Process-Time`` covers the full processing pipeline including request-ID
assignment.
"""

import time
from typing import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

#: Response header name.
_HEADER = "X-Process-Time"


class TimingMiddleware(BaseHTTPMiddleware):
    """Records and reports HTTP request processing time.

    Adds ``X-Process-Time: <seconds>`` (e.g. ``0.0042``) to every response.
    Uses ``time.perf_counter()`` for sub-millisecond precision.
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        start: float = time.perf_counter()
        response: Response = await call_next(request)
        elapsed: float = time.perf_counter() - start
        response.headers[_HEADER] = f"{elapsed:.4f}"
        return response
