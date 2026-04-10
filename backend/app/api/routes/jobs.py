from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.models import Company, Job, Match
from app.models.enums import JobStatus, Trade
from app.schemas.auth import TokenData
from app.schemas.job import JobCreate, JobDetailRead, JobListRead, JobStatusUpdate

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("", response_model=list[JobListRead])
async def list_jobs(
    status: JobStatus | None = None,
    trade: Trade | None = None,
    zone: str | None = None,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """List all jobs with optional filters for status, trade, and zone."""
    stmt = select(Job)

    if status is not None:
        stmt = stmt.where(Job.status == status)
    if trade is not None:
        stmt = stmt.where(Job.trade_required == trade)
    if zone is not None:
        stmt = stmt.where(Job.zone == zone)

    stmt = stmt.order_by(Job.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{job_id}", response_model=JobDetailRead)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Get a single job with its company name and match count."""
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get company name
    company_stmt = select(Company.name).where(Company.id == job.company_id)
    company_name = (await db.execute(company_stmt)).scalar() or ""

    # Get match count
    match_count_stmt = select(func.count()).select_from(Match).where(Match.job_id == job_id)
    match_count = (await db.execute(match_count_stmt)).scalar() or 0

    data = JobDetailRead.model_validate(job)
    data.company_name = company_name
    data.match_count = match_count
    return data


@router.post("", response_model=JobDetailRead, status_code=201)
async def create_job(
    data: JobCreate,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Create a new job posting for a company."""
    job = Job(**data.model_dump())
    db.add(job)
    await db.commit()
    await db.refresh(job)

    # Get company name for response
    company_stmt = select(Company.name).where(Company.id == job.company_id)
    company_name = (await db.execute(company_stmt)).scalar() or ""

    result = JobDetailRead.model_validate(job)
    result.company_name = company_name
    return result


@router.patch("/{job_id}/status", response_model=JobDetailRead)
async def update_job_status(
    job_id: UUID,
    data: JobStatusUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Update a job's status (e.g. open -> matching -> filled -> completed)."""
    stmt = select(Job).where(Job.id == job_id)
    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    job.status = data.status
    await db.commit()
    await db.refresh(job)

    company_stmt = select(Company.name).where(Company.id == job.company_id)
    company_name = (await db.execute(company_stmt)).scalar() or ""

    match_count_stmt = select(func.count()).select_from(Match).where(Match.job_id == job_id)
    match_count = (await db.execute(match_count_stmt)).scalar() or 0

    result = JobDetailRead.model_validate(job)
    result.company_name = company_name
    result.match_count = match_count
    return result
