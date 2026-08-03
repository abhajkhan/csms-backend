"""Worker Pydantic schemas.

Per CSMS_SPEC.md §6.4 & 03_API_CONTRACT.md §8.
"""

from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class WorkerCreate(BaseModel):
    """Schema for registering a new worker."""

    full_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Worker's full name.",
        examples=["Ramesh Kumar"],
    )
    daily_wage: Decimal = Field(
        ...,
        gt=0,
        max_digits=12,
        decimal_places=2,
        description="Standard daily wage rate in ₹ (must be greater than 0).",
        examples=[500.00],
    )

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Worker full name cannot be blank.")
        return cleaned


class WorkerUpdate(BaseModel):
    """Schema for updating worker details."""

    full_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Updated worker name.",
    )
    daily_wage: Decimal | None = Field(
        default=None,
        gt=0,
        max_digits=12,
        decimal_places=2,
        description="Updated daily wage rate in ₹.",
    )

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, value: str | None) -> str | None:
        if value is not None:
            cleaned = value.strip()
            if not cleaned:
                raise ValueError("Worker full name cannot be blank.")
            return cleaned
        return value


class WorkerResponse(BaseModel):
    """Schema for worker detail responses."""

    model_config = ConfigDict(from_attributes=True)

    worker_id: int = Field(..., description="Unique worker ID.")
    full_name: str = Field(..., description="Worker's full name.")
    daily_wage: Decimal = Field(..., description="Daily wage rate.")
    is_active: bool = Field(..., description="Active account status.")
    created_by: int = Field(..., description="User ID of creator.")


class WorkerListResponse(BaseModel):
    """Schema for paginated worker list responses."""

    items: list[WorkerResponse] = Field(..., description="Page items.")
    total: int = Field(..., description="Total matching worker records.")
    page: int = Field(..., description="Current page number.")
    page_size: int = Field(..., description="Items per page.")
    total_pages: int = Field(..., description="Total number of pages.")
