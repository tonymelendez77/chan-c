import logging
from datetime import datetime, timezone

import httpx

from app.core.config import settings
from app.models.enums import WorkerReply

logger = logging.getLogger(__name__)

VAPI_BASE_URL = "https://api.vapi.ai"


def _build_assistant_prompt(
    worker_name: str,
    job_trade: str,
    job_zone: str,
    job_start: str,
    job_end: str,
    job_daily_rate: str,
    company_name: str,
    call_type: str,
) -> str:
    """Build the system prompt for the Vapi assistant based on call type."""
    if call_type == "counteroffer":
        return (
            f"Eres un asistente de CHAN-C. Llamas a {worker_name} "
            f"porque quiere hacer una contrapropuesta para un trabajo "
            f"de {job_trade} en Zona {job_zone} con {company_name}. "
            f"El trabajo ofrece Q{job_daily_rate} por dia. "
            f"Pregunta: que precio propone, que fechas le convienen, "
            f"y si tiene alguna condicion especial. "
            f"Se amable, claro y breve. Maximo 3 minutos."
        )
    # Default: confirmation
    return (
        f"Eres un asistente de CHAN-C. Llamas a {worker_name} "
        f"para confirmar su interes en un trabajo de {job_trade} "
        f"en Zona {job_zone} del {job_start} al {job_end} "
        f"a Q{job_daily_rate} por dia con {company_name}. "
        f"Pregunta que puede cubrir y que no puede cubrir. "
        f"Pregunta sobre su disponibilidad exacta. "
        f"Se amable, claro y breve. Maximo 3 minutos."
    )


def _format_phone(phone: str) -> str:
    """Add +502 prefix to Guatemalan 8-digit numbers."""
    phone = phone.strip()
    if phone.startswith("+"):
        return phone
    if phone.startswith("502"):
        return f"+{phone}"
    return f"+502{phone}"


async def initiate_call(match, worker, job, company_name: str) -> str:
    """Initiate a Vapi voice call to a worker. Returns the vapi_call_id.

    Raises on API failure so the caller can handle it.
    """
    call_type = "counteroffer" if match.worker_reply == WorkerReply.contra else "confirmation"

    trade_es = {
        "electrician": "electricista", "plumber": "plomero",
        "carpenter": "carpintero", "mason": "albañil",
        "painter": "pintor", "welder": "soldador",
        "roofer": "techador", "general_labor": "ayudante",
        "security": "seguridad", "housemaid": "limpieza",
        "gardener": "jardinero", "other": "trabajo",
    }
    job_trade = trade_es.get(job.trade_required.value, "trabajo")

    prompt = _build_assistant_prompt(
        worker_name=worker.full_name,
        job_trade=job_trade,
        job_zone=job.zone,
        job_start=job.start_date.strftime("%d/%m"),
        job_end=job.end_date.strftime("%d/%m"),
        job_daily_rate=str(int(job.daily_rate)),
        company_name=company_name,
        call_type=call_type,
    )

    payload = {
        "phoneNumberId": settings.VAPI_PHONE_NUMBER_ID,
        "customer": {
            "number": _format_phone(worker.phone),
        },
        "assistant": {
            "model": {
                "provider": "anthropic",
                "model": "claude-sonnet-4-20250514",
                "messages": [{"role": "system", "content": prompt}],
            },
            "voice": {
                "provider": "11labs",
                "voiceId": "21m00Tcm4TlvDq8ikWAM",
            },
            "language": "es-GT",
            "firstMessage": f"Hola, buenas. Hablo con {worker.full_name}?",
            "maxDurationSeconds": 180,
        },
        "metadata": {
            "match_id": str(match.id),
            "worker_id": str(worker.id),
            "call_type": call_type,
        },
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{VAPI_BASE_URL}/call/phone",
            json=payload,
            headers={
                "Authorization": f"Bearer {settings.VAPI_API_KEY}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()

    vapi_call_id = data.get("id", "")
    logger.info("Vapi call initiated: %s (type=%s, worker=%s)", vapi_call_id, call_type, worker.id)
    return vapi_call_id


async def get_call_status(vapi_call_id: str) -> dict:
    """Fetch call status, transcript, and recording from Vapi.

    Returns a dict with keys: status, transcript, duration_seconds,
    recording_url, ended_at.
    """
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{VAPI_BASE_URL}/call/{vapi_call_id}",
            headers={"Authorization": f"Bearer {settings.VAPI_API_KEY}"},
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()

    # Map Vapi statuses to our statuses
    vapi_status = data.get("status", "")
    transcript = data.get("transcript", "")
    recording_url = data.get("recordingUrl", "")
    duration = data.get("duration", None)
    ended_at_str = data.get("endedAt", None)

    ended_at = None
    if ended_at_str:
        try:
            ended_at = datetime.fromisoformat(ended_at_str.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            ended_at = datetime.now(timezone.utc)

    return {
        "status": vapi_status,
        "transcript": transcript,
        "duration_seconds": int(duration) if duration else None,
        "recording_url": recording_url,
        "ended_at": ended_at,
    }
