"""CSMS Backend — FastAPI application entry point.

Wires together:
    - Application settings and structured logging
    - CORS, Request-ID, Timing, and Request-Logging middleware
    - Custom exception handlers
    - API v1 router
    - Root and health check endpoints

Middleware registration order matters: Starlette processes middleware in
reverse registration order (last-added runs first).  The desired execution
order is:

    Request  →  RequestID  →  Timing  →  RequestLogging  →  CORS  →  handler
    Response ←  RequestID  ←  Timing  ←  RequestLogging  ←  CORS  ←  handler

Register in the opposite order so the last-added (RequestID) runs first.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router as v1_router
from app.core.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.middleware.logging import RequestLoggingMiddleware
from app.middleware.request_id import RequestIDMiddleware
from app.middleware.timing import TimingMiddleware

# ─── Bootstrap logging before anything else ─────────────────────────────────
settings = get_settings()
configure_logging(level=10 if settings.DEBUG else 20)  # DEBUG=10, INFO=20
logger = get_logger(__name__)


# ─── Lifespan ────────────────────────────────────────────────────────────────


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Handle application startup and shutdown events."""
    logger.info(
        "Starting %s v%s [%s]",
        settings.PROJECT_NAME,
        settings.VERSION,
        settings.ENVIRONMENT,
    )
    yield
    logger.info("Shutting down %s.", settings.PROJECT_NAME)


# ─── Application ─────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=(
        "REST API for the Construction Site Management System. "
        "Manages labour, attendance, expenses, warehouse inventory, "
        "and purchase activity across construction sites."
    ),
    version=settings.VERSION,
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─── Exception handlers ──────────────────────────────────────────────────────
# Register before middleware so handlers can access request state.

register_exception_handlers(app)

# ─── Middleware stack (registered in reverse execution order) ─────────────────
# Execution order: RequestID → Timing → RequestLogging → CORS → route handler

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(RequestIDMiddleware)

# ─── Routers ─────────────────────────────────────────────────────────────────

app.include_router(v1_router, prefix="/api/v1")


# ─── Root endpoints ──────────────────────────────────────────────────────────


@app.get("/", tags=["Root"], summary="API root")
def root() -> dict:
    """Return basic API information."""
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Root"], summary="Health check")
def health_check() -> dict:
    """Return service health status.

    Used by load balancers and monitoring systems.
    Always returns 200 while the process is alive.
    """
    return {"status": "healthy", "project": settings.PROJECT_NAME}
