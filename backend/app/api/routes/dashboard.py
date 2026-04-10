from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.models import Company, Job, Match, Worker
from app.models.enums import JobStatus, MatchStatus
from app.schemas.auth import TokenData
from app.schemas.dashboard import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Return overview counts for the admin dashboard home page."""
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    active_workers = (
        await db.execute(
            select(func.count()).select_from(Worker).where(Worker.is_active.is_(True))
        )
    ).scalar() or 0

    vetted_workers = (
        await db.execute(
            select(func.count())
            .select_from(Worker)
            .where(Worker.is_active.is_(True), Worker.is_vetted.is_(True))
        )
    ).scalar() or 0

    open_jobs = (
        await db.execute(
            select(func.count())
            .select_from(Job)
            .where(Job.status.in_([JobStatus.open, JobStatus.matching]))
        )
    ).scalar() or 0

    active_matches = (
        await db.execute(
            select(func.count())
            .select_from(Match)
            .where(Match.status == MatchStatus.accepted)
        )
    ).scalar() or 0

    pending_matches = (
        await db.execute(
            select(func.count())
            .select_from(Match)
            .where(
                Match.status.in_([
                    MatchStatus.pending_company,
                    MatchStatus.pending_worker,
                    MatchStatus.pending_review,
                    MatchStatus.pending_company_decision,
                ])
            )
        )
    ).scalar() or 0

    completed_jobs_this_month = (
        await db.execute(
            select(func.count())
            .select_from(Job)
            .where(Job.status == JobStatus.completed, Job.updated_at >= month_start)
        )
    ).scalar() or 0

    total_companies = (
        await db.execute(select(func.count()).select_from(Company))
    ).scalar() or 0

    return DashboardStats(
        active_workers=active_workers,
        vetted_workers=vetted_workers,
        open_jobs=open_jobs,
        active_matches=active_matches,
        pending_matches=pending_matches,
        completed_jobs_this_month=completed_jobs_this_month,
        total_companies=total_companies,
    )
