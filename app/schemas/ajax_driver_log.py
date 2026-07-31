"""AjaxDriverLog Pydantic schemas.

Per CSMS_SPEC.md §6.9 & §12
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AjaxDriverLogCreate(BaseModel):
    site_id: int
    date: date
    num_mixes: int = Field(gt=0, description="Number of mixes completed")
    note: str | None = None


class AjaxDriverLogResponse(BaseModel):
    log_id: int
    driver_id: int
    site_id: int
    date: date
    num_mixes: int
    rate_per_mix: Decimal
    total_amount: Decimal
    expense_id: int | None = None
    note: str | None = None

    model_config = ConfigDict(from_attributes=True)
