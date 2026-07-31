"""WorkerPayment Pydantic schemas.

Per CSMS_SPEC.md §6.7 & §12
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.constants.enums import PaymentType


class WorkerPaymentBase(BaseModel):
    worker_id: int
    amount: Decimal
    payment_type: PaymentType
    note: str | None = None


class WorkerPaymentCreate(WorkerPaymentBase):
    pass


class WorkerPaymentResponse(WorkerPaymentBase):
    payment_id: int
    paid_by: int
    paid_at: datetime

    model_config = ConfigDict(from_attributes=True)
