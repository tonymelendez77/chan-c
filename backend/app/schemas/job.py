from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import JobStatus, SkillLevelRequired, Trade


class JobBase(BaseModel):
    title: str
    trade_required: Trade
    skill_level_required: SkillLevelRequired
    zone: str
    start_date: date
    end_date: date
    daily_rate: float
    currency: str = "GTQ"
    headcount: int = 1
    description: str
    special_requirements: str | None = None


class JobCreate(JobBase):
    company_id: UUID
    created_by: UUID
    status: JobStatus = JobStatus.open


class JobStatusUpdate(BaseModel):
    status: JobStatus


class JobListRead(BaseModel):
    id: UUID
    company_id: UUID
    title: str
    trade_required: Trade
    skill_level_required: SkillLevelRequired
    zone: str
    start_date: date
    end_date: date
    daily_rate: float
    currency: str
    headcount: int
    status: JobStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class JobDetailRead(JobListRead):
    description: str
    special_requirements: str | None = None
    created_by: UUID
    updated_at: datetime
    company_name: str = ""
    match_count: int = 0

    model_config = {"from_attributes": True}
