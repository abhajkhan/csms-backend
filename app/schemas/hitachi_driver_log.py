"""HitachiDriverLog Pydantic schemas.

Per CSMS_SPEC.md §6.10 & §12
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class HitachiDriverLogCreate(BaseModel):
    site_id: int
    date: date
    hours_worked: Decimal = Field(gt=0, description="Hours worked")
    note: str | None = None


class HitachiDriverLogResponse(BaseModel):
    log_id: int
    driver_id: int
    site_id: int
    date: date
    hours_worked: Decimal
    hourly_rate: Decimal
    total_amount: Decimal
    expense_id: int | None = None
    note: str | None = None

    model_config = ConfigDict(from_attributes=True)
