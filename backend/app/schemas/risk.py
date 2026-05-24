from pydantic import BaseModel
from datetime import datetime


class RiskRecordCreate(BaseModel):
    student_id: str
    risk_level: str
    reason: str = ""


class RiskRecordUpdate(BaseModel):
    status: str | None = None
    risk_level: str | None = None
    reason: str | None = None


class RiskRecordResponse(BaseModel):
    id: str
    student_id: str
    risk_level: str
    reason: str
    status: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
    model_config = {"from_attributes": True}


class RiskStats(BaseModel):
    high: int
    medium: int
    low: int
    total: int
