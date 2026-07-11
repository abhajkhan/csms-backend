"""CSMS Backend — FastAPI application entry point.

Wires together:
    - Application settings
    - Structured logging
    - CORS middleware
    - API v1 router
    - Root and health check endpoints
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router as v1_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger

# ─── Bootstrap logging before anything else ─────────────────────────────────
configure_logging()
logger = get_logger(__name__)

settings = get_settings()


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

# ─── CORS ────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
