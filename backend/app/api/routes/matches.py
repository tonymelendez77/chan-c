from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.models import Company, Job, Match, Worker
from app.models.enums import MatchStatus
from app.schemas.auth import TokenData
from app.schemas.match import (
    MatchCreate,
    MatchDetailRead,
    MatchListRead,
    MatchStatusUpdate,
)

router = APIRouter(prefix="/matches", tags=["matches"])

PENDING_STATUSES = [
    MatchStatus.pending_company,
    MatchStatus.pending_worker,
    MatchStatus.pending_review,
    MatchStatus.pending_company_decision,
]


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


@router.post("", response_model=MatchDetailRead, status_code=201)
async def create_match(
    data: MatchCreate,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Create a new match linking a worker to a job. Used by admins during manual matching."""
    # Verify worker and job exist
    worker = (await db.execute(select(Worker).where(Worker.id == data.worker_id))).scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")

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
    """Update match status and optionally record worker reply or final rate."""
    stmt = select(Match).where(Match.id == match_id)
    result = await db.execute(stmt)
    match = result.scalar_one_or_none()
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")

    match.status = data.status
    if data.worker_reply is not None:
        match.worker_reply = data.worker_reply
    if data.final_rate is not None:
        match.final_rate = data.final_rate

    await db.commit()
    await db.refresh(match)
    return await _enrich_match(match, db)
