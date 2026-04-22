from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, require_admin
from app.models import Company, Job, Match, Payment, Worker
from app.models.enums import JobStatus, PaymentStatus
from app.schemas.auth import TokenData
from app.schemas.payment import BillingStats, PaymentListItem

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/stats", response_model=BillingStats)
async def billing_stats(
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Aggregated commission totals for the admin billing dashboard."""
    month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0).date()

    pending = (await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0))
        .where(Payment.status.in_([PaymentStatus.pending, PaymentStatus.invoiced, PaymentStatus.overdue]))
    )).scalar() or 0

    collected = (await db.execute(
        select(func.coalesce(func.sum(Payment.amount), 0))
        .where(Payment.status == PaymentStatus.paid, Payment.paid_date >= month_start)
    )).scalar() or 0

    avg = (await db.execute(
        select(func.coalesce(func.avg(Payment.amount), 0))
        .where(Payment.invoice_date >= month_start)
    )).scalar() or 0

    active_value = (await db.execute(
        select(func.coalesce(func.sum(Job.total_value), 0))
        .where(Job.status.in_([JobStatus.open, JobStatus.matching, JobStatus.filled]))
    )).scalar() or 0

    return BillingStats(
        commissions_pending=Decimal(str(pending)),
        commissions_collected=Decimal(str(collected)),
        average_commission=Decimal(str(avg)),
        total_job_value_active=Decimal(str(active_value)),
    )


@router.get("", response_model=list[PaymentListItem])
async def list_commissions(
    status: PaymentStatus | None = None,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """List commissions with enriched company/worker/job info."""
    stmt = select(Payment)
    if status is not None:
        stmt = stmt.where(Payment.status == status)
    stmt = stmt.order_by(Payment.invoice_date.desc().nulls_last(), Payment.created_at.desc())
    payments = (await db.execute(stmt)).scalars().all()

    response: list[PaymentListItem] = []
    for p in payments:
        item = PaymentListItem.model_validate(p)
        company_name = (await db.execute(select(Company.name).where(Company.id == p.company_id))).scalar()
        item.company_name = company_name or ""

        match = (await db.execute(select(Match).where(Match.id == p.match_id))).scalar_one_or_none()
        if match:
            worker = (await db.execute(select(Worker.full_name).where(Worker.id == match.worker_id))).scalar()
            item.worker_name = worker or ""
            job = (await db.execute(select(Job.title, Job.trade_required).where(Job.id == match.job_id))).one_or_none()
            if job:
                item.job_title = job.title
                item.trade = job.trade_required.value if job.trade_required else None
        response.append(item)
    return response


@router.patch("/{payment_id}/mark-paid", response_model=PaymentListItem)
async def mark_payment_paid(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Mark a pending/invoiced commission as paid."""
    payment = (await db.execute(select(Payment).where(Payment.id == payment_id))).scalar_one_or_none()
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")

    payment.status = PaymentStatus.paid
    payment.paid_date = date.today()
    await db.commit()
    await db.refresh(payment)

    item = PaymentListItem.model_validate(payment)
    company_name = (await db.execute(select(Company.name).where(Company.id == payment.company_id))).scalar()
    item.company_name = company_name or ""
    return item
