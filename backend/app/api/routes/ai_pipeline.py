from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, require_admin
from app.models import AICall, AIExtraction, Worker
from app.models.enums import AICallStatus, AICallType
from app.schemas.ai_pipeline import (
    AICallDetailRead,
    AICallListRead,
    ExtractionRead,
    ReviewRequest,
    TriggerResponse,
)
from app.schemas.auth import TokenData
from app.services import ai_pipeline

router = APIRouter(prefix="/ai", tags=["ai-pipeline"])


@router.post("/trigger-calls", response_model=TriggerResponse)
async def trigger_calls(
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Manually trigger processing of all pending AI calls. Initiates Vapi calls for each pending match."""
    count = await ai_pipeline.process_pending_ai_calls(db)
    return TriggerResponse(detail="Calls initiated", count=count)


@router.post("/process-completed", response_model=TriggerResponse)
async def process_completed(
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Manually trigger processing of completed calls. Fetches transcripts and runs extraction."""
    count = await ai_pipeline.process_completed_calls(db)
    return TriggerResponse(detail="Calls processed", count=count)


@router.get("/calls", response_model=list[AICallListRead])
async def list_calls(
    status: AICallStatus | None = None,
    call_type: AICallType | None = None,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """List all AI calls with optional filters for status and call type."""
    stmt = select(AICall)

    if status is not None:
        stmt = stmt.where(AICall.status == status)
    if call_type is not None:
        stmt = stmt.where(AICall.call_type == call_type)

    stmt = stmt.order_by(AICall.created_at.desc())
    result = await db.execute(stmt)
    calls = result.scalars().all()

    # Enrich with worker info
    response = []
    for call in calls:
        data = AICallListRead.model_validate(call)
        worker_stmt = select(Worker.full_name, Worker.phone).where(Worker.id == call.worker_id)
        worker_row = (await db.execute(worker_stmt)).one_or_none()
        if worker_row:
            data.worker_name = worker_row.full_name
            data.worker_phone = worker_row.phone
        response.append(data)

    return response


@router.get("/calls/{call_id}", response_model=AICallDetailRead)
async def get_call(
    call_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Get a single AI call with full transcript and extraction data."""
    stmt = (
        select(AICall)
        .where(AICall.id == call_id)
        .options(selectinload(AICall.extractions))
    )
    result = await db.execute(stmt)
    call = result.scalar_one_or_none()
    if call is None:
        raise HTTPException(status_code=404, detail="AI call not found")

    data = AICallDetailRead.model_validate(call)

    worker_stmt = select(Worker.full_name, Worker.phone).where(Worker.id == call.worker_id)
    worker_row = (await db.execute(worker_stmt)).one_or_none()
    if worker_row:
        data.worker_name = worker_row.full_name
        data.worker_phone = worker_row.phone

    return data


@router.patch("/calls/{call_id}/review", response_model=ExtractionRead)
async def review_call(
    call_id: UUID,
    data: ReviewRequest,
    db: AsyncSession = Depends(get_db),
    admin: TokenData = Depends(require_admin),
):
    """Admin reviews a flagged call and corrects the extraction data."""
    # Find the most recent extraction for this call
    stmt = (
        select(AIExtraction)
        .where(AIExtraction.call_id == call_id)
        .order_by(AIExtraction.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    extraction = result.scalar_one_or_none()
    if extraction is None:
        raise HTTPException(status_code=404, detail="No extraction found for this call")

    # Apply corrections
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(extraction, field, value)

    extraction.requires_admin_review = False
    extraction.reviewed_by = admin.user_id
    extraction.reviewed_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(extraction)
    return extraction
