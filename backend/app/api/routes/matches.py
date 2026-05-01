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

    # Send WhatsApp match notification to the company
    try:
        await _notify_company_of_match(db, match, worker, job)
    except Exception:
        # Don't block match creation if WhatsApp fails
        pass

    return await _enrich_match(match, db)


async def _notify_company_of_match(db: AsyncSession, match: Match, worker: Worker, job: Job) -> None:
    """Send WhatsApp match notification to the company and set their conversation state."""
    from app.models import WhatsAppConversation
    from app.services import whatsapp as wa_service
    from sqlalchemy.orm.attributes import flag_modified

    company = (await db.execute(select(Company).where(Company.id == job.company_id))).scalar_one_or_none()
    if company is None:
        return

    conv_stmt = select(WhatsAppConversation).where(WhatsAppConversation.phone == company.phone)
    conv = (await db.execute(conv_stmt)).scalar_one_or_none()
    if conv is None:
        return  # company hasn't engaged via WhatsApp yet

    # Worker primary trade for tools
    from app.models import WorkerTrade
    wtrade = (await db.execute(select(WorkerTrade).where(WorkerTrade.worker_id == worker.id).limit(1))).scalar_one_or_none()
    tools_friendly = {
        "own_tools": "Tiene sus herramientas",
        "partial_tools": "Tiene algunas herramientas",
        "needs_tools": "Necesita herramientas",
        "depends_on_job": "Depende del trabajo",
    }
    tools_text = tools_friendly.get(wtrade.tools_status, "—") if wtrade else "—"

    can_cover = "\n".join([f"  • {c}" for c in (wtrade.can_cover or [])]) if wtrade else ""
    cannot_cover = "\n".join([f"  • {c}" for c in (wtrade.cannot_cover or [])]) if wtrade else ""

    parts = worker.full_name.split()
    display_name = parts[0] + (f" {parts[-1][0]}." if len(parts) > 1 else "")

    trade_es = {
        "electrician": "Electricista", "plumber": "Plomero", "mason": "Albañil",
        "carpenter": "Carpintero", "painter": "Pintor", "welder": "Soldador",
        "roofer": "Techador", "general_labor": "Ayudante", "security": "Seguridad",
        "housemaid": "Limpieza", "gardener": "Jardinero", "other": "Trabajo",
    }.get(job.trade_required.value, str(job.trade_required.value))

    msg = (
        f"👷 *Encontramos un match* para tu trabajo de {trade_es} en Zona {job.zone}:\n\n"
        f"*{display_name}*\n"
        f"⭐ {worker.rating_avg:.1f} · {worker.total_jobs} trabajos\n\n"
    )
    if can_cover:
        msg += f"✅ Puede cubrir:\n{can_cover}\n\n"
    if cannot_cover:
        msg += f"❌ No puede cubrir:\n{cannot_cover}\n\n"
    msg += (
        f"🔧 Herramientas: {tools_text}\n"
        f"💰 Q{int(match.offered_rate)}/día\n\n"
        "¿Qué decides?\n\n"
        "Escribe *ACEPTAR* para contratar\n"
        "Escribe *OTRO* para pedir otro trabajador"
    )

    await wa_service.send_whatsapp(db, company.phone, msg)

    # Update conversation state
    conv.state = "company_pending_match_decision"
    merged = dict(conv.data or {})
    merged["pending_match_id"] = str(match.id)
    conv.data = merged
    flag_modified(conv, "data")
    await db.commit()


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
