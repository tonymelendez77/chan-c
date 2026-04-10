from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import (
    Language,
    ProfileStatus,
    ReferenceOutcome,
    SkillLevel,
    Trade,
)


# --- Worker Trade ---

class WorkerTradeBase(BaseModel):
    trade: Trade
    skill_level: SkillLevel
    years_experience: int
    can_cover: list[str] | None = None
    cannot_cover: list[str] | None = None
    verified_by_admin: bool = False


class WorkerTradeCreate(WorkerTradeBase):
    pass


class WorkerTradeRead(WorkerTradeBase):
    id: UUID
    worker_id: UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Worker Reference ---

class WorkerReferenceBase(BaseModel):
    reference_name: str
    reference_phone: str
    relationship: str
    call_date: date | None = None
    outcome: ReferenceOutcome | None = None
    notes: str | None = None


class WorkerReferenceCreate(WorkerReferenceBase):
    pass


class WorkerReferenceRead(WorkerReferenceBase):
    id: UUID
    worker_id: UUID
    checked_by: UUID | None = None

    model_config = {"from_attributes": True}


# --- Worker Profile ---

class WorkerProfileBase(BaseModel):
    bio: str | None = None
    initial_score: float | None = None
    profile_status: ProfileStatus = ProfileStatus.pending_review
    profile_url: str | None = None


class WorkerProfileCreate(WorkerProfileBase):
    pass


class WorkerProfileRead(WorkerProfileBase):
    id: UUID
    worker_id: UUID
    verified_at: datetime | None = None
    total_earnings: float = 0
    response_rate: float = 0
    completion_rate: float = 0

    model_config = {"from_attributes": True}


# --- Worker ---

class WorkerBase(BaseModel):
    full_name: str
    phone: str
    dpi: str | None = None
    zone: str
    language: Language = Language.spanish
    is_available: bool = True
    notes: str | None = None


class WorkerCreate(WorkerBase):
    trades: list[WorkerTradeCreate] | None = None
    references: list[WorkerReferenceCreate] | None = None
    profile: WorkerProfileCreate | None = None


class WorkerUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    dpi: str | None = None
    zone: str | None = None
    language: Language | None = None
    is_available: bool | None = None
    is_vetted: bool | None = None
    notes: str | None = None


class WorkerListRead(BaseModel):
    """Lightweight worker for list views."""
    id: UUID
    full_name: str
    phone: str
    zone: str
    language: Language
    is_available: bool
    is_active: bool
    is_vetted: bool
    rating_avg: float
    total_jobs: int
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkerDetailRead(WorkerListRead):
    """Full worker with nested trades, references, profile."""
    dpi: str | None = None
    vetting_date: date | None = None
    vetted_by: UUID | None = None
    notes: str | None = None
    profile: WorkerProfileRead | None = None
    trades: list[WorkerTradeRead] = []
    references: list[WorkerReferenceRead] = []

    model_config = {"from_attributes": True}
