from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import AICallStatus, AICallType, ExtractionFinalStatus


class AICallListRead(BaseModel):
    id: UUID
    match_id: UUID | None = None
    worker_id: UUID
    call_type: AICallType
    vapi_call_id: str | None = None
    status: AICallStatus
    duration_seconds: int | None = None
    created_at: datetime
    worker_name: str = ""
    worker_phone: str = ""

    model_config = {"from_attributes": True}


class ExtractionRead(BaseModel):
    id: UUID
    call_id: UUID
    can_cover: list[str] | None = None
    cannot_cover: list[str] | None = None
    counteroffer_price: float | None = None
    counteroffer_dates: str | None = None
    counteroffer_notes: str | None = None
    availability_notes: str | None = None
    final_status: ExtractionFinalStatus | None = None
    confidence_score: float | None = None
    requires_admin_review: bool = False
    reviewed_by: UUID | None = None
    reviewed_at: datetime | None = None
    extraction_model: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AICallDetailRead(AICallListRead):
    transcript: str | None = None
    recording_url: str | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    extractions: list[ExtractionRead] = []

    model_config = {"from_attributes": True}


class TriggerResponse(BaseModel):
    detail: str
    count: int


class ReviewRequest(BaseModel):
    can_cover: list[str] | None = None
    cannot_cover: list[str] | None = None
    counteroffer_price: float | None = None
    counteroffer_dates: str | None = None
    counteroffer_notes: str | None = None
    availability_notes: str | None = None
    final_status: ExtractionFinalStatus | None = None
    confidence_score: float | None = None
