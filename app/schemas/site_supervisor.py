"""SiteSupervisor Pydantic schemas.

Per CSMS_SPEC.md §6.3 & §12
"""

from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict


class SiteSupervisorBase(BaseModel):
    site_id: int
    supervisor_id: int


class SiteSupervisorCreate(SiteSupervisorBase):
    pass


class SiteSupervisorResponse(SiteSupervisorBase):
    id: int
    assigned_at: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
