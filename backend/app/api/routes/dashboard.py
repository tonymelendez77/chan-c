from datetime import datetime, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.models import Company, Job, Match, Payment, Worker
from app.models.enums import JobStatus, MatchStatus, PaymentStatus
from app.schemas.auth import TokenData
from app.schemas.dashboard import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Return overview counts + commission totals for the admin dashboard home page."""
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

    # --- Commission stats (10% business model) ---
    commissions_pending = (
        await db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0))
            .where(Payment.status.in_([PaymentStatus.pending, PaymentStatus.invoiced, PaymentStatus.overdue]))
        )
    ).scalar() or 0

    commissions_collected = (
        await db.execute(
            select(func.coalesce(func.sum(Payment.amount), 0))
            .where(Payment.status == PaymentStatus.paid, Payment.paid_date >= month_start.date())
        )
    ).scalar() or 0

    avg_row = (
        await db.execute(
            select(func.coalesce(func.avg(Payment.amount), 0))
            .where(Payment.invoice_date >= month_start.date())
        )
    ).scalar() or 0

    total_job_value_active = (
        await db.execute(
            select(func.coalesce(func.sum(Job.total_value), 0))
            .where(Job.status.in_([JobStatus.open, JobStatus.matching, JobStatus.filled]))
        )
    ).scalar() or 0

    return DashboardStats(
        active_workers=active_workers,
        vetted_workers=vetted_workers,
        open_jobs=open_jobs,
        active_matches=active_matches,
        pending_matches=pending_matches,
        completed_jobs_this_month=completed_jobs_this_month,
        total_companies=total_companies,
        commissions_pending=Decimal(str(commissions_pending)),
        commissions_collected=Decimal(str(commissions_collected)),
        average_commission=Decimal(str(avg_row)),
        total_job_value_active=Decimal(str(total_job_value_active)),
    )
