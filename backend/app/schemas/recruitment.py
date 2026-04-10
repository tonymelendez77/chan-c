from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import (
    AICallStatus,
    Language,
    OnboardingCallType,
    ProfileStatus,
    ReferenceCallStatus,
    ReferenceOutcome,
    SkillLevel,
    Trade,
)


class RecruitmentPipelineStats(BaseModel):
    sms_received: int
    intake_calls_pending: int
    intake_calls_completed: int
    references_pending: int
    pending_admin_review: int
    approved_this_month: int
    rejected_this_month: int


class OnboardingCallRead(BaseModel):
    id: UUID
    call_type: OnboardingCallType
    status: AICallStatus
    vapi_call_id: str | None = None
    transcript: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReferenceCallRead(BaseModel):
    id: UUID
    reference_name: str
    reference_phone: str
    call_status: ReferenceCallStatus
    outcome: ReferenceOutcome | None = None
    ai_summary: str | None = None
    confidence_score: float | None = None
    called_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class WorkerTradeRead(BaseModel):
    id: UUID
    trade: Trade
    skill_level: SkillLevel
    years_experience: int
    can_cover: list[str] | None = None
    cannot_cover: list[str] | None = None

    model_config = {"from_attributes": True}


class WorkerProfileRead(BaseModel):
    id: UUID
    bio: str | None = None
    initial_score: float | None = None
    profile_status: ProfileStatus
    total_earnings: float = 0
    response_rate: float = 0
    completion_rate: float = 0

    model_config = {"from_attributes": True}


class WorkerReferenceRead(BaseModel):
    id: UUID
    reference_name: str
    reference_phone: str
    relationship: str
    outcome: ReferenceOutcome | None = None
    notes: str | None = None

    model_config = {"from_attributes": True}


class WorkerRecruitmentDetail(BaseModel):
    id: UUID
    full_name: str
    phone: str
    dpi: str | None = None
    zone: str
    language: Language
    is_active: bool
    is_vetted: bool
    vetting_date: date | None = None
    created_at: datetime
    profile: WorkerProfileRead | None = None
    trades: list[WorkerTradeRead] = []
    references: list[WorkerReferenceRead] = []
    onboarding_calls: list[OnboardingCallRead] = []
    reference_calls: list[ReferenceCallRead] = []

    model_config = {"from_attributes": True}


class PendingWorkerRead(BaseModel):
    id: UUID
    full_name: str
    phone: str
    zone: str
    language: Language
    created_at: datetime
    profile_status: ProfileStatus | None = None
    initial_score: float | None = None
    intake_completed: bool = False
    reference_count: int = 0

    model_config = {"from_attributes": True}


class ApproveRejectRequest(BaseModel):
    message: str | None = None


class TriggerResponse(BaseModel):
    detail: str
    count: int
