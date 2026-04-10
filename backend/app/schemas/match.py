from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import MatchStatus, WorkerReply


class MatchCreate(BaseModel):
    job_id: UUID
    worker_id: UUID
    created_by: UUID
    offered_rate: float
    status: MatchStatus = MatchStatus.pending_worker


class MatchStatusUpdate(BaseModel):
    status: MatchStatus
    worker_reply: WorkerReply | None = None
    final_rate: float | None = None


class MatchListRead(BaseModel):
    id: UUID
    job_id: UUID
    worker_id: UUID
    status: MatchStatus
    offered_rate: float
    final_rate: float | None = None
    worker_reply: WorkerReply | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MatchDetailRead(MatchListRead):
    created_by: UUID
    company_notified_at: datetime | None = None
    worker_sms_sent_at: datetime | None = None
    worker_replied_at: datetime | None = None
    company_decided_at: datetime | None = None
    worker_name: str = ""
    worker_phone: str = ""
    job_title: str = ""
    company_name: str = ""

    model_config = {"from_attributes": True}
