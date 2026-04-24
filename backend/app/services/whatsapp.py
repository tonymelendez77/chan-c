from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from twilio.rest import Client

from app.core.config import settings
from app.models import SMSLog
from app.models.enums import SMSDirection, SMSStatus, Trade


def _twilio_client() -> Client:
    return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def _format_whatsapp(phone: str) -> str:
    """Format phone for Twilio WhatsApp: whatsapp:+502XXXXXXXX."""
    phone = phone.strip()
    if phone.startswith("whatsapp:"):
        return phone
    if phone.startswith("+"):
        return f"whatsapp:{phone}"
    if phone.startswith("502"):
        return f"whatsapp:+{phone}"
    return f"whatsapp:+502{phone}"


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


async def _log_whatsapp(
    db: AsyncSession,
    *,
    worker_id: UUID | None,
    match_id: UUID | None,
    direction: SMSDirection,
    message: str,
    twilio_sid: str | None,
    status: SMSStatus,
) -> SMSLog:
    """Write a WhatsApp message to sms_logs."""
    log = SMSLog(
        worker_id=worker_id,
        match_id=match_id,
        direction=direction,
        message=f"[WhatsApp] {message}",
        twilio_sid=twilio_sid,
        status=status,
        sent_at=datetime.now(timezone.utc),
    )
    db.add(log)
    await db.flush()
    return log


async def send_whatsapp(
    db: AsyncSession,
    to_phone: str,
    message: str,
    *,
    worker_id: UUID | None = None,
    match_id: UUID | None = None,
) -> str | None:
    """Send an outbound WhatsApp message via Twilio and log it. Returns the Twilio SID."""
    client = _twilio_client()
    tw_msg = client.messages.create(
        to=_format_whatsapp(to_phone),
        from_=settings.TWILIO_WHATSAPP_NUMBER,
        body=message,
    )
    await _log_whatsapp(
        db,
        worker_id=worker_id,
        match_id=match_id,
        direction=SMSDirection.outbound,
        message=message,
        twilio_sid=tw_msg.sid,
        status=SMSStatus.sent,
    )
    return tw_msg.sid


async def send_whatsapp_job_offer(db: AsyncSession, worker, match, job) -> str | None:
    """Send a rich-format WhatsApp job offer to a worker. Always includes tools section."""
    trade = _trade_name(job.trade_required)
    if getattr(job, "tools_provided", False):
        tools_line = "\U0001f527 *Herramientas:* La empresa provee todo"
    else:
        tools_line = "\U0001f527 *Herramientas:* Debes traer las tuyas"
    msg = (
        f"\U0001f44b Hola {worker.full_name}.\n\n"
        f"\U0001f4bc *Trabajo disponible*\n"
        f"Oficio: {trade}\n"
        f"Zona: {job.zone}\n"
        f"Fechas: {job.start_date.strftime('%d/%m')} al {job.end_date.strftime('%d/%m')}\n"
        f"Pago: Q{int(job.daily_rate)}/d\u00eda\n"
        f"{tools_line}\n\n"
        f"Responde *SI*, *NO* o *CONTRA*"
    )
    return await send_whatsapp(
        db, worker.phone, msg, worker_id=worker.id, match_id=match.id
    )


async def send_whatsapp_job_confirmed(
    db: AsyncSession, worker, job, company_phone: str
) -> str | None:
    """Send WhatsApp confirmation with company contact."""
    trade = _trade_name(job.trade_required)
    msg = (
        f"\u2705 *Confirmado*\n"
        f"Oficio: {trade} en Zona {job.zone}\n"
        f"Contacto empresa: {company_phone}"
    )
    return await send_whatsapp(db, worker.phone, msg, worker_id=worker.id)


async def send_whatsapp_job_declined(db: AsyncSession, worker) -> str | None:
    """Acknowledge worker declining via WhatsApp."""
    msg = "Entendido. Te avisaremos del pr\u00f3ximo trabajo. \U0001f44d"
    return await send_whatsapp(db, worker.phone, msg, worker_id=worker.id)


async def send_whatsapp_counteroffer_call_notice(db: AsyncSession, worker) -> str | None:
    """Tell worker we'll call about their counteroffer via WhatsApp."""
    msg = "Gracias. Te llamamos para conocer tu propuesta. \U0001f4de"
    return await send_whatsapp(db, worker.phone, msg, worker_id=worker.id)


async def send_whatsapp_rating_request(
    db: AsyncSession, worker, company_name: str
) -> str | None:
    """Ask the worker to rate the completed job via WhatsApp."""
    msg = (
        f"\u00bfC\u00f3mo fue el trabajo con {company_name}?\n"
        f"Responde *SI* (bien) o *NO* (problema) \U0001f31f"
    )
    return await send_whatsapp(db, worker.phone, msg, worker_id=worker.id)


async def send_whatsapp_pause_confirmation(db: AsyncSession, worker) -> str | None:
    """Confirm via WhatsApp that worker's offers are paused."""
    msg = (
        "\u23f8\ufe0f *Ofertas pausadas*\n"
        f"Entendido {worker.full_name}. Pausamos tus ofertas.\n"
        "Cuando est\u00e9s listo escribe *REANUDAR*."
    )
    return await send_whatsapp(db, worker.phone, msg, worker_id=worker.id)


async def send_whatsapp_resume_confirmation(db: AsyncSession, worker) -> str | None:
    """Confirm via WhatsApp that worker's offers are reactivated."""
    msg = (
        "\u25b6\ufe0f *Ofertas reactivadas*\n"
        f"Bienvenido de vuelta {worker.full_name}.\n"
        "Te avisamos cuando haya trabajo para ti. \U0001f4aa"
    )
    return await send_whatsapp(db, worker.phone, msg, worker_id=worker.id)


async def send_whatsapp_intake_notice(db: AsyncSession, worker) -> str | None:
    """Send WhatsApp intake notice to new worker."""
    msg = (
        "\U0001f44b Hola. Gracias por tu inter\u00e9s en CHAN-C.\n"
        "En unos minutos te llamamos para una\n"
        "entrevista r\u00e1pida. Ten listo tu DPI. \U0001f4cb"
    )
    return await send_whatsapp(db, worker.phone, msg, worker_id=worker.id)


async def log_inbound_whatsapp(
    db: AsyncSession,
    *,
    worker_id: UUID | None,
    match_id: UUID | None,
    message: str,
    twilio_sid: str | None = None,
) -> SMSLog:
    """Log an inbound WhatsApp message from a worker."""
    return await _log_whatsapp(
        db,
        worker_id=worker_id,
        match_id=match_id,
        direction=SMSDirection.inbound,
        message=message,
        twilio_sid=twilio_sid,
        status=SMSStatus.received,
    )
