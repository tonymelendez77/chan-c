from datetime import date
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.models import Company, Job, Match, Payment, Worker
from app.models.enums import MatchStatus, PaymentStatus, PaymentType
from app.schemas.auth import TokenData
from app.schemas.match import (
    MatchCreate,
    MatchDetailRead,
    MatchListRead,
    MatchStatusUpdate,
)
from app.schemas.payment import CommissionBreakdown

router = APIRouter(prefix="/matches", tags=["matches"])

PENDING_STATUSES = [
    MatchStatus.pending_company,
    MatchStatus.pending_worker,
    MatchStatus.pending_review,
    MatchStatus.pending_company_decision,
]

COMMISSION_PCT = Decimal("10.0")


def calculate_commission(job: Job, match: Match) -> tuple[Decimal, Decimal, int]:
    """Return (job_value, commission_amount, duration_days) for a match.

    Uses final_rate if set (counteroffer accepted), otherwise offered_rate.
    job_value = daily_rate × duration_days × headcount
    commission_amount = job_value × 10%
    """
    daily_rate = Decimal(str(match.final_rate or match.offered_rate))
    duration_days = (job.end_date - job.start_date).days + 1
    headcount = int(job.headcount or 1)
    job_value = daily_rate * Decimal(duration_days) * Decimal(headcount)
    commission_amount = (job_value * COMMISSION_PCT / Decimal("100")).quantize(Decimal("0.01"))
    return job_value, commission_amount, duration_days


async def _enrich_match(match: Match, db: AsyncSession) -> MatchDetailRead:
    """Add worker name/phone, job title, and company name to a match response."""
    data = MatchDetailRead.model_validate(match)

    worker_stmt = select(Worker.full_name, Worker.phone).where(Worker.id == match.worker_id)
    worker_row = (await db.execute(worker_stmt)).one_or_none()
    if worker_row:
        data.worker_name = worker_row.full_name
        data.worker_phone = worker_row.phone

    job_stmt = select(Job.title, Job.company_id).where(Job.id == match.job_id)
    job_row = (await db.execute(job_stmt)).one_or_none()
    if job_row:
        data.job_title = job_row.title
        company_stmt = select(Company.name).where(Company.id == job_row.company_id)
        data.company_name = (await db.execute(company_stmt)).scalar() or ""

    return data


@router.get("/pending", response_model=list[MatchListRead])
async def list_pending_matches(
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """List all matches that need admin attention (pending statuses)."""
    stmt = (
        select(Match)
        .where(Match.status.in_(PENDING_STATUSES))
        .order_by(Match.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("", response_model=list[MatchListRead])
async def list_matches(
    status: MatchStatus | None = None,
    job_id: UUID | None = None,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """List all matches with optional filters for status and job."""
    stmt = select(Match)

    if status is not None:
        stmt = stmt.where(Match.status == status)
    if job_id is not None:
        stmt = stmt.where(Match.job_id == job_id)

    stmt = stmt.order_by(Match.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{match_id}", response_model=MatchDetailRead)
async def get_match(
    match_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Get a single match with full details including worker, job, and company info."""
    stmt = select(Match).where(Match.id == match_id)
    result = await db.execute(stmt)
    match = result.scalar_one_or_none()
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    return await _enrich_match(match, db)


@router.get("/{match_id}/commission", response_model=CommissionBreakdown)
async def get_match_commission(
    match_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Return the commission breakdown for a match (10% of daily_rate × days × headcount)."""
    match = (await db.execute(select(Match).where(Match.id == match_id))).scalar_one_or_none()
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")
    job = (await db.execute(select(Job).where(Job.id == match.job_id))).scalar_one()

    job_value, commission_amount, duration_days = calculate_commission(job, match)
    payment = (await db.execute(select(Payment).where(Payment.match_id == match.id))).scalar_one_or_none()

    return CommissionBreakdown(
        daily_rate=Decimal(str(match.final_rate or match.offered_rate)),
        duration_days=duration_days,
        headcount=int(job.headcount),
        job_value=job_value,
        commission_pct=COMMISSION_PCT,
        commission_amount=commission_amount,
        currency=job.currency or "GTQ",
        status=payment.status.value if payment else "not_created",
    )


@router.post("", response_model=MatchDetailRead, status_code=201)
async def create_match(
    data: MatchCreate,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Create a new match linking a worker to a job. Used by admins during manual matching."""
    worker = (await db.execute(select(Worker).where(Worker.id == data.worker_id))).scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")

    if getattr(worker, "paused", False):
        raise HTTPException(
            status_code=400,
            detail="Este trabajador pausó sus ofertas. No puede recibir matches hasta que reactive.",
        )

    job = (await db.execute(select(Job).where(Job.id == data.job_id))).scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    match = Match(**data.model_dump())
    db.add(match)
    await db.commit()
    await db.refresh(match)
    return await _enrich_match(match, db)


@router.patch("/{match_id}/status", response_model=MatchDetailRead)
async def update_match_status(
    match_id: UUID,
    data: MatchStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Update match status. On first acceptance, auto-creates a commission Payment (10% of job value)."""
    stmt = select(Match).where(Match.id == match_id)
    result = await db.execute(stmt)
    match = result.scalar_one_or_none()
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")

    previous_status = match.status
    match.status = data.status
    if data.worker_reply is not None:
        match.worker_reply = data.worker_reply
    if data.final_rate is not None:
        match.final_rate = data.final_rate

    # Auto-create commission payment when match is accepted for the first time
    if data.status == MatchStatus.accepted and previous_status != MatchStatus.accepted:
        existing = (await db.execute(select(Payment).where(Payment.match_id == match.id))).scalar_one_or_none()
        if existing is None:
            job = (await db.execute(select(Job).where(Job.id == match.job_id))).scalar_one()
            job_value, commission_amount, _ = calculate_commission(job, match)
            payment = Payment(
                match_id=match.id,
                company_id=job.company_id,
                amount=commission_amount,
                job_value=job_value,
                commission_pct=COMMISSION_PCT,
                currency=job.currency or "GTQ",
                payment_type=PaymentType.commission,
                status=PaymentStatus.pending,
                invoice_date=date.today(),
            )
            db.add(payment)
            job.total_value = job_value

    await db.commit()
    await db.refresh(match)
    return await _enrich_match(match, db)
