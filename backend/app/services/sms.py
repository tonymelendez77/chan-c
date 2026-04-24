from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from twilio.rest import Client

from app.core.config import settings
from app.models import SMSLog
from app.models.enums import SMSDirection, SMSStatus, Trade


def _twilio_client() -> Client:
    return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def _format_phone(phone: str) -> str:
    """Add +502 prefix to Guatemalan 8-digit numbers if not already prefixed."""
    phone = phone.strip()
    if phone.startswith("+"):
        return phone
    if phone.startswith("502"):
        return f"+{phone}"
    return f"+502{phone}"


_TRADE_ES = {
    Trade.electrician: "electricista",
    Trade.plumber: "plomero",
    Trade.carpenter: "carpintero",
    Trade.mason: "albañil",
    Trade.painter: "pintor",
    Trade.welder: "soldador",
    Trade.roofer: "techador",
    Trade.general_labor: "ayudante",
    Trade.security: "seguridad",
    Trade.housemaid: "limpieza",
    Trade.gardener: "jardinero",
    Trade.other: "trabajo",
}


def _trade_name(trade: Trade) -> str:
    return _TRADE_ES.get(trade, "trabajo")


async def _log_sms(
    db: AsyncSession,
    *,
    worker_id: UUID | None,
    match_id: UUID | None,
    direction: SMSDirection,
    message: str,
    twilio_sid: str | None,
    status: SMSStatus,
) -> SMSLog:
    """Write a row to sms_logs."""
    log = SMSLog(
        worker_id=worker_id,
        match_id=match_id,
        direction=direction,
        message=message,
        twilio_sid=twilio_sid,
        status=status,
        sent_at=datetime.now(timezone.utc),
    )
    db.add(log)
    await db.flush()
    return log


async def send_sms(
    db: AsyncSession,
    to_phone: str,
    message: str,
    *,
    worker_id: UUID | None = None,
    match_id: UUID | None = None,
) -> str | None:
    """Send an outbound SMS via Twilio and log it. Returns the Twilio SID."""
    client = _twilio_client()
    tw_msg = client.messages.create(
        to=_format_phone(to_phone),
        from_=settings.TWILIO_PHONE_NUMBER,
        body=message,
    )
    await _log_sms(
        db,
        worker_id=worker_id,
        match_id=match_id,
        direction=SMSDirection.outbound,
        message=message,
        twilio_sid=tw_msg.sid,
        status=SMSStatus.sent,
    )
    return tw_msg.sid


async def send_job_offer(db: AsyncSession, worker, match, job) -> str | None:
    """Send a formatted job offer SMS to a worker. Adds tools info if under 160 chars."""
    trade = _trade_name(job.trade_required)
    msg = (
        f"Hola {worker.full_name}. Trabajo de {trade} en Zona {job.zone}. "
        f"{job.start_date.strftime('%d/%m')} al {job.end_date.strftime('%d/%m')}. "
        f"Q{int(job.daily_rate)}/dia. Responde SI, NO o CONTRA."
    )
    # Append tools info only if it fits in the remaining budget
    tools_line = None
    if getattr(job, "tools_provided", False):
        tools_line = "Herramientas incluidas."
    elif getattr(job, "tools_provided", None) is False:
        tools_line = "Debes traer tus herramientas."
    if tools_line and len(msg) + 1 + len(tools_line) <= 160:
        msg = f"{msg} {tools_line}"

    return await send_sms(
        db, worker.phone, msg, worker_id=worker.id, match_id=match.id
    )


async def send_job_confirmed(
    db: AsyncSession, worker, job, company_phone: str
) -> str | None:
    """Send confirmation SMS with company contact info."""
    trade = _trade_name(job.trade_required)
    msg = (
        f"Confirmado. Trabajo de {trade} en Zona {job.zone}. "
        f"Contacto empresa: {company_phone}"
    )
    return await send_sms(db, worker.phone, msg, worker_id=worker.id)


async def send_job_declined(db: AsyncSession, worker) -> str | None:
    """Acknowledge a worker declining a job offer."""
    msg = "Entendido. Te avisaremos del proximo trabajo."
    return await send_sms(db, worker.phone, msg, worker_id=worker.id)


async def send_counteroffer_received(db: AsyncSession, worker) -> str | None:
    """Tell the worker we received their counteroffer."""
    msg = "Recibimos tu contrapropuesta. Te contactamos pronto."
    return await send_sms(db, worker.phone, msg, worker_id=worker.id)


async def send_counteroffer_call_notice(db: AsyncSession, worker) -> str | None:
    """Tell the worker we'll call them to discuss their counteroffer."""
    msg = "Gracias. Te llamamos para conocer tu propuesta."
    return await send_sms(db, worker.phone, msg, worker_id=worker.id)


async def send_rating_request(
    db: AsyncSession, worker, company_name: str
) -> str | None:
    """Ask the worker to rate the completed job."""
    msg = (
        f"Como fue el trabajo con {company_name}? "
        f"Responde SI (bien) o NO (problema)."
    )
    return await send_sms(db, worker.phone, msg, worker_id=worker.id)


async def send_pause_confirmation(db: AsyncSession, worker) -> str | None:
    """Confirm to worker that their job offers are paused."""
    msg = f"Entendido {worker.full_name}. Pausamos tus ofertas. Escribe REANUDAR cuando estes listo."
    return await send_sms(db, worker.phone, msg, worker_id=worker.id)


async def send_resume_confirmation(db: AsyncSession, worker) -> str | None:
    """Confirm to worker that their job offers are active again."""
    msg = f"Bienvenido de vuelta {worker.full_name}. Tus ofertas estan activas. Te avisamos pronto."
    return await send_sms(db, worker.phone, msg, worker_id=worker.id)


async def send_offer_via_preferred_channel(db: AsyncSession, worker, match, job) -> str | None:
    """Send job offer via worker's preferred channel. Defaults to SMS if WhatsApp not enabled."""
    if getattr(worker, "whatsapp_enabled", False):
        from app.services import whatsapp
        return await whatsapp.send_whatsapp_job_offer(db, worker, match, job)
    return await send_job_offer(db, worker, match, job)


async def log_inbound_sms(
    db: AsyncSession,
    *,
    worker_id: UUID | None,
    match_id: UUID | None,
    message: str,
    twilio_sid: str | None = None,
) -> SMSLog:
    """Log an inbound SMS from a worker."""
    return await _log_sms(
        db,
        worker_id=worker_id,
        match_id=match_id,
        direction=SMSDirection.inbound,
        message=message,
        twilio_sid=twilio_sid,
        status=SMSStatus.received,
    )
