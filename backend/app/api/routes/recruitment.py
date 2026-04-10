from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, require_admin
from app.models import (
    ReferenceCall,
    Worker,
    WorkerOnboardingCall,
    WorkerProfile,
    WorkerReference,
)
from app.models.enums import (
    AICallStatus,
    OnboardingCallType,
    ProfileStatus,
    ReferenceCallStatus,
)
from app.schemas.auth import TokenData
from app.schemas.recruitment import (
    ApproveRejectRequest,
    OnboardingCallRead,
    PendingWorkerRead,
    RecruitmentPipelineStats,
    ReferenceCallRead,
    TriggerResponse,
    WorkerRecruitmentDetail,
)
from app.services import intake_service, sms as sms_service

router = APIRouter(prefix="/recruitment", tags=["recruitment"])


@router.get("/pipeline", response_model=RecruitmentPipelineStats)
async def get_pipeline_stats(
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Overview of the recruitment funnel with counts at each stage."""
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Workers created this month (from TRABAJAR SMS)
    sms_received = (await db.execute(
        select(func.count()).select_from(Worker).where(Worker.created_at >= month_start)
    )).scalar() or 0

    intake_calls_pending = (await db.execute(
        select(func.count()).select_from(WorkerOnboardingCall).where(
            WorkerOnboardingCall.call_type == OnboardingCallType.intake,
            WorkerOnboardingCall.status.in_([AICallStatus.initiated, AICallStatus.in_progress]),
        )
    )).scalar() or 0

    intake_calls_completed = (await db.execute(
        select(func.count()).select_from(WorkerOnboardingCall).where(
            WorkerOnboardingCall.call_type == OnboardingCallType.intake,
            WorkerOnboardingCall.status == AICallStatus.completed,
        )
    )).scalar() or 0

    references_pending = (await db.execute(
        select(func.count()).select_from(ReferenceCall).where(
            ReferenceCall.call_status == ReferenceCallStatus.pending,
        )
    )).scalar() or 0

    pending_admin_review = (await db.execute(
        select(func.count()).select_from(WorkerProfile).where(
            WorkerProfile.profile_status == ProfileStatus.pending_review,
        )
    )).scalar() or 0

    approved_this_month = (await db.execute(
        select(func.count()).select_from(Worker).where(
            Worker.is_vetted.is_(True),
            Worker.vetting_date >= month_start.date(),
        )
    )).scalar() or 0

    rejected_this_month = (await db.execute(
        select(func.count()).select_from(WorkerProfile).where(
            WorkerProfile.profile_status == ProfileStatus.suspended,
        )
    )).scalar() or 0

    return RecruitmentPipelineStats(
        sms_received=sms_received,
        intake_calls_pending=intake_calls_pending,
        intake_calls_completed=intake_calls_completed,
        references_pending=references_pending,
        pending_admin_review=pending_admin_review,
        approved_this_month=approved_this_month,
        rejected_this_month=rejected_this_month,
    )


@router.get("/pending", response_model=list[PendingWorkerRead])
async def list_pending_workers(
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """List workers with profile_status = pending_review for admin review."""
    stmt = (
        select(Worker, WorkerProfile)
        .join(WorkerProfile, WorkerProfile.worker_id == Worker.id)
        .where(WorkerProfile.profile_status == ProfileStatus.pending_review)
        .order_by(Worker.created_at.desc())
    )
    rows = (await db.execute(stmt)).all()

    results = []
    for worker, profile in rows:
        # Check if intake call completed
        intake_stmt = select(func.count()).select_from(WorkerOnboardingCall).where(
            WorkerOnboardingCall.worker_id == worker.id,
            WorkerOnboardingCall.call_type == OnboardingCallType.intake,
            WorkerOnboardingCall.status == AICallStatus.completed,
        )
        intake_completed = ((await db.execute(intake_stmt)).scalar() or 0) > 0

        ref_count_stmt = select(func.count()).select_from(WorkerReference).where(
            WorkerReference.worker_id == worker.id,
        )
        ref_count = (await db.execute(ref_count_stmt)).scalar() or 0

        results.append(PendingWorkerRead(
            id=worker.id,
            full_name=worker.full_name,
            phone=worker.phone,
            zone=worker.zone,
            language=worker.language,
            created_at=worker.created_at,
            profile_status=profile.profile_status,
            initial_score=float(profile.initial_score) if profile.initial_score else None,
            intake_completed=intake_completed,
            reference_count=ref_count,
        ))

    return results


@router.get("/{worker_id}", response_model=WorkerRecruitmentDetail)
async def get_recruitment_detail(
    worker_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Full recruitment detail for one worker including all calls and extractions."""
    stmt = (
        select(Worker)
        .where(Worker.id == worker_id)
        .options(
            selectinload(Worker.profile),
            selectinload(Worker.trades),
            selectinload(Worker.references),
            selectinload(Worker.onboarding_calls),
            selectinload(Worker.reference_calls),
        )
    )
    worker = (await db.execute(stmt)).scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")

    return worker


@router.post("/trigger-intake-calls", response_model=TriggerResponse)
async def trigger_intake_calls(
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Manually trigger processing of completed intake calls."""
    count = await intake_service.process_completed_intake_calls(db)
    return TriggerResponse(detail="Intake calls processed", count=count)


@router.post("/trigger-reference-calls", response_model=TriggerResponse)
async def trigger_reference_calls(
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Manually trigger processing of completed reference calls."""
    count = await intake_service.process_completed_reference_calls(db)
    return TriggerResponse(detail="Reference calls processed", count=count)


@router.post("/{worker_id}/approve", status_code=200)
async def approve_worker(
    worker_id: UUID,
    data: ApproveRejectRequest | None = None,
    db: AsyncSession = Depends(get_db),
    admin: TokenData = Depends(require_admin),
):
    """Admin manually approves a worker. Sets active, vetted, and sends approval SMS."""
    worker = (await db.execute(select(Worker).where(Worker.id == worker_id))).scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")

    worker.is_active = True
    worker.is_vetted = True
    worker.vetting_date = datetime.now(timezone.utc).date()
    worker.vetted_by = admin.user_id

    profile = (await db.execute(
        select(WorkerProfile).where(WorkerProfile.worker_id == worker_id)
    )).scalar_one_or_none()
    if profile:
        profile.profile_status = ProfileStatus.active
        profile.verified_at = datetime.now(timezone.utc)

    await sms_service.send_sms(
        db, worker.phone,
        f"Bienvenido a CHAN-C {worker.full_name}. Tu perfil fue aprobado. Te avisamos cuando haya trabajo.",
        worker_id=worker.id,
    )

    await db.commit()
    return {"detail": f"Worker {worker.full_name} approved"}


@router.post("/{worker_id}/reject", status_code=200)
async def reject_worker(
    worker_id: UUID,
    data: ApproveRejectRequest | None = None,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Admin manually rejects a worker. Sets inactive and suspended."""
    worker = (await db.execute(select(Worker).where(Worker.id == worker_id))).scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")

    worker.is_active = False

    profile = (await db.execute(
        select(WorkerProfile).where(WorkerProfile.worker_id == worker_id)
    )).scalar_one_or_none()
    if profile:
        profile.profile_status = ProfileStatus.suspended

    if data and data.message:
        await sms_service.send_sms(
            db, worker.phone, data.message, worker_id=worker.id,
        )

    await db.commit()
    return {"detail": f"Worker {worker.full_name} rejected"}
