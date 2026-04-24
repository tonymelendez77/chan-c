import json
import logging
from datetime import datetime, timezone

import anthropic
import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import (
    ReferenceCall,
    Worker,
    WorkerOnboardingCall,
    WorkerProfile,
    WorkerReference,
    WorkerTrade,
)
from app.models.enums import (
    AICallStatus,
    Language,
    OnboardingCallType,
    ProfileStatus,
    ReferenceCallStatus,
    ReferenceOutcome,
    SkillLevel,
    Trade,
)
from app.services import sms as sms_service

logger = logging.getLogger(__name__)

VAPI_BASE_URL = "https://api.vapi.ai"
EXTRACTION_MODEL = "claude-sonnet-4-20250514"

INTAKE_PROMPT = (
    "Eres un asistente amable de CHAN-C, una plataforma de trabajo en Guatemala. "
    "Llamas a un trabajador que quiere registrarse. Necesitas obtener: "
    "1. Nombre completo "
    "2. Numero de DPI "
    "3. Zona donde vive actualmente en Guatemala "
    "4. Zonas donde prefiere trabajar (puede decir todas si no tiene preferencia) "
    "5. Zonas o sectores donde NO quiere trabajar (puede decir ninguna si no tiene restricciones) "
    "6. Oficio principal (electricista, plomero, carpintero, albanil, pintor, "
    "soldador, techador, ayudante, seguridad, limpieza, jardinero, otro) "
    "7. Nivel de experiencia (junior, intermedio, senior) "
    "8. Anos de experiencia "
    "9. Que trabajos puede cubrir "
    "10. Herramientas de trabajo: ¿tiene sus propias herramientas? "
    "Por ejemplo taladro, sierra, nivel, llaves, etc. Opciones: "
    "(a) tengo todas mis herramientas, "
    "(b) tengo algunas, necesito otras, "
    "(c) no tengo, la empresa debe proveer, "
    "(d) depende del tipo de trabajo "
    "11. Que trabajos NO puede cubrir "
    "12. Tarifa diaria esperada en quetzales "
    "13. Disponibilidad (dias y horas) "
    "14. Idioma preferido (espanol, kiche, mam, otro) "
    "15. Hasta 3 referencias: nombre y telefono de cada una "
    "Se amable, claro y paciente. Maximo 8 minutos. "
    "Si no entiende algo, explica de forma simple."
)

INTAKE_EXTRACTION_SYSTEM = (
    "Eres un asistente de extraccion de datos para CHAN-C en Guatemala. "
    "Extrae informacion de una entrevista telefonica con un trabajador informal. "
    "La conversacion es en espanol. "
    "Devuelve SOLO JSON valido. Sin explicacion ni markdown. "
    "Si un campo no fue mencionado usa null."
)

INTAKE_EXTRACTION_SCHEMA = """\
Extract the following from the transcript and return as JSON:
{
  "full_name": string or null,
  "dpi": string or null,
  "zone": string or null,
  "preferred_zones": ["list of preferred work zones"] or [],
  "excluded_zones": ["list of zones they refuse to work in"] or [],
  "trade": "electrician"|"plumber"|"carpenter"|"mason"|"painter"|"welder"|"roofer"|"general_labor"|"security"|"housemaid"|"gardener"|"other" or null,
  "skill_level": "junior"|"mid"|"senior" or null,
  "years_experience": number or null,
  "can_cover": ["list of strings"],
  "cannot_cover": ["list of strings"],
  "tools_status": "own_tools"|"needs_tools"|"partial_tools"|"depends_on_job" or null,
  "tools_notes": "description of what they have and need" or null,
  "daily_rate": number or null,
  "availability_notes": string or null,
  "language": "spanish"|"kiche"|"mam"|"other",
  "references": [{"name": string, "phone": string}],
  "confidence_score": 0.0 to 1.0
}
"""

REFERENCE_EXTRACTION_SCHEMA = """\
Extract the following from the transcript and return as JSON:
{
  "outcome": "positive"|"neutral"|"negative",
  "summary": "brief summary of what reference said",
  "confidence_score": 0.0 to 1.0,
  "recommends": true or false
}
"""


def _format_phone(phone: str) -> str:
    phone = phone.strip()
    if phone.startswith("+"):
        return phone
    if phone.startswith("502"):
        return f"+{phone}"
    return f"+502{phone}"


# ---------- Intake Call ----------

async def initiate_intake_call(db: AsyncSession, worker: Worker) -> str:
    """Initiate a Vapi intake interview call. Returns vapi_call_id."""
    payload = {
        "phoneNumberId": settings.VAPI_PHONE_NUMBER_ID,
        "customer": {"number": _format_phone(worker.phone)},
        "assistant": {
            "model": {
                "provider": "anthropic",
                "model": "claude-sonnet-4-20250514",
                "messages": [{"role": "system", "content": INTAKE_PROMPT}],
            },
            "voice": {"provider": "11labs", "voiceId": "21m00Tcm4TlvDq8ikWAM"},
            "language": "es-GT",
            "firstMessage": "Hola, buenas. Te llamo de CHAN-C para registrarte como trabajador. Tienes unos minutos?",
            "maxDurationSeconds": 480,
        },
        "metadata": {"worker_id": str(worker.id), "call_type": "intake"},
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

    # Update onboarding call record
    stmt = (
        select(WorkerOnboardingCall)
        .where(
            WorkerOnboardingCall.worker_id == worker.id,
            WorkerOnboardingCall.call_type == OnboardingCallType.intake,
            WorkerOnboardingCall.status == AICallStatus.initiated,
        )
        .order_by(WorkerOnboardingCall.created_at.desc())
        .limit(1)
    )
    call = (await db.execute(stmt)).scalar_one_or_none()
    if call:
        call.vapi_call_id = vapi_call_id
        call.status = AICallStatus.in_progress
        call.started_at = datetime.now(timezone.utc)

    logger.info("Intake call initiated: %s for worker %s", vapi_call_id, worker.id)
    return vapi_call_id


# ---------- Intake Extraction ----------

async def extract_intake_data(transcript: str) -> dict:
    """Send intake transcript to Claude API and extract structured worker data."""
    if not transcript or len(transcript.strip()) < 30:
        logger.warning("Intake transcript too short (len=%d)", len(transcript or ""))
        return {"confidence_score": 0.0, "references": []}

    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=EXTRACTION_MODEL,
            max_tokens=1024,
            system=INTAKE_EXTRACTION_SYSTEM,
            messages=[{"role": "user", "content": f"{INTAKE_EXTRACTION_SCHEMA}\n\nTranscript:\n{transcript}"}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3].strip()
        result = json.loads(raw)
        result.setdefault("confidence_score", 0.5)
        result.setdefault("references", [])
        return result

    except Exception as e:
        logger.error("Intake extraction failed: %s", e)
        return {"confidence_score": 0.0, "references": []}


# ---------- Apply Extraction ----------

_TRADE_MAP = {
    "electrician": Trade.electrician, "plumber": Trade.plumber,
    "carpenter": Trade.carpenter, "mason": Trade.mason,
    "painter": Trade.painter, "welder": Trade.welder,
    "roofer": Trade.roofer, "general_labor": Trade.general_labor,
    "security": Trade.security, "housemaid": Trade.housemaid,
    "gardener": Trade.gardener, "other": Trade.other,
}

_SKILL_MAP = {"junior": SkillLevel.junior, "mid": SkillLevel.mid, "senior": SkillLevel.senior}

_LANG_MAP = {"spanish": Language.spanish, "kiche": Language.kiche, "mam": Language.mam, "other": Language.other}


async def apply_intake_extraction(
    db: AsyncSession, worker: Worker, extraction: dict
) -> None:
    """Apply extracted data to worker, trades, references, and profile."""
    # Update worker fields
    if extraction.get("full_name"):
        worker.full_name = extraction["full_name"]
    if extraction.get("dpi"):
        worker.dpi = extraction["dpi"]
    if extraction.get("zone"):
        worker.zone = extraction["zone"]
    lang_str = extraction.get("language", "spanish")
    worker.language = _LANG_MAP.get(lang_str, Language.spanish)

    # Create trade record
    trade_str = extraction.get("trade")
    if trade_str and trade_str in _TRADE_MAP:
        skill_str = extraction.get("skill_level", "junior")
        years = extraction.get("years_experience") or 0
        tools_status_raw = extraction.get("tools_status")
        if tools_status_raw not in {"own_tools", "needs_tools", "partial_tools", "depends_on_job"}:
            tools_status_raw = None
        trade = WorkerTrade(
            worker_id=worker.id,
            trade=_TRADE_MAP[trade_str],
            skill_level=_SKILL_MAP.get(skill_str, SkillLevel.junior),
            years_experience=int(years),
            can_cover=extraction.get("can_cover"),
            cannot_cover=extraction.get("cannot_cover"),
            tools_status=tools_status_raw,
            tools_notes=extraction.get("tools_notes"),
        )
        db.add(trade)

    # Create reference records
    for ref in extraction.get("references", [])[:3]:
        name = ref.get("name", "").strip()
        phone = ref.get("phone", "").strip()
        if name and phone:
            worker_ref = WorkerReference(
                worker_id=worker.id,
                reference_name=name,
                reference_phone=phone,
                relationship="laboral",
            )
            db.add(worker_ref)

    # Update profile
    stmt = select(WorkerProfile).where(WorkerProfile.worker_id == worker.id)
    profile = (await db.execute(stmt)).scalar_one_or_none()
    if profile:
        daily_rate = extraction.get("daily_rate")
        availability = extraction.get("availability_notes", "")
        can_cover = ", ".join(extraction.get("can_cover", []))
        cannot_cover = ", ".join(extraction.get("cannot_cover", []))
        bio = f"Oficio: {trade_str or 'N/A'}. Puede cubrir: {can_cover or 'N/A'}. No puede: {cannot_cover or 'N/A'}."
        if daily_rate:
            bio += f" Tarifa: Q{daily_rate}/dia."
        if availability:
            bio += f" Disponibilidad: {availability}."
        # TODO: Add preferred_zones and excluded_zones columns to WorkerProfile model,
        # then store these as proper array fields instead of embedding in bio.
        preferred_zones = extraction.get("preferred_zones", [])
        excluded_zones = extraction.get("excluded_zones", [])
        if preferred_zones:
            bio += f" Zonas preferidas: {', '.join(preferred_zones)}."
        if excluded_zones:
            bio += f" Zonas excluidas: {', '.join(excluded_zones)}."
        profile.bio = bio
        profile.initial_score = extraction.get("confidence_score", 0.0)

    logger.info("Intake extraction applied for worker %s", worker.id)


# ---------- Profile Scoring ----------

def calculate_profile_score(
    extraction: dict, reference_outcomes: list[str]
) -> float:
    """Calculate a 0-1 profile score from intake data and reference outcomes."""
    score = 0.0

    # Base from intake confidence (0-0.5)
    confidence = float(extraction.get("confidence_score", 0.0))
    score += min(confidence, 1.0) * 0.5

    # References: +0.1 per positive, -0.1 per negative (max contribution 0.3)
    ref_score = 0.0
    for outcome in reference_outcomes:
        if outcome == "positive":
            ref_score += 0.1
        elif outcome == "negative":
            ref_score -= 0.1
    score += max(min(ref_score, 0.3), -0.3)

    # DPI bonus
    if extraction.get("dpi"):
        score += 0.2

    return max(0.0, min(1.0, score))


# ---------- Reference Calls ----------

async def initiate_reference_call(
    db: AsyncSession, worker: Worker, reference: WorkerReference
) -> str:
    """Initiate a Vapi call to verify a worker's reference. Returns vapi_call_id."""
    prompt = (
        f"Eres un asistente de CHAN-C, una plataforma de trabajo en Guatemala. "
        f"Llamas para verificar una referencia laboral de {worker.full_name}. "
        f"Necesitas saber: "
        f"1. Confirmar que conocen a {worker.full_name} "
        f"2. En que trabajaron juntos "
        f"3. Como fue su desempeno y puntualidad "
        f"4. Si lo recomendarian para trabajos de construccion "
        f"Se breve y amable. Maximo 3 minutos."
    )

    payload = {
        "phoneNumberId": settings.VAPI_PHONE_NUMBER_ID,
        "customer": {"number": _format_phone(reference.reference_phone)},
        "assistant": {
            "model": {
                "provider": "anthropic",
                "model": "claude-sonnet-4-20250514",
                "messages": [{"role": "system", "content": prompt}],
            },
            "voice": {"provider": "11labs", "voiceId": "21m00Tcm4TlvDq8ikWAM"},
            "language": "es-GT",
            "firstMessage": f"Hola, buenas. Le llamo de CHAN-C. Tenemos una referencia laboral de {worker.full_name}. Tiene un momento?",
            "maxDurationSeconds": 180,
        },
        "metadata": {
            "worker_id": str(worker.id),
            "reference_id": str(reference.id),
            "call_type": "reference_check",
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

    # Create reference call record
    ref_call = ReferenceCall(
        worker_id=worker.id,
        reference_name=reference.reference_name,
        reference_phone=reference.reference_phone,
        call_status=ReferenceCallStatus.pending,
        called_at=datetime.now(timezone.utc),
    )
    db.add(ref_call)
    await db.flush()

    # Also create an onboarding call record for tracking
    onboarding_call = WorkerOnboardingCall(
        worker_id=worker.id,
        call_type=OnboardingCallType.reference_check,
        vapi_call_id=vapi_call_id,
        status=AICallStatus.in_progress,
        started_at=datetime.now(timezone.utc),
    )
    db.add(onboarding_call)

    logger.info("Reference call initiated: %s for worker %s ref %s",
                vapi_call_id, worker.id, reference.reference_name)
    return vapi_call_id


async def extract_reference_outcome(transcript: str) -> dict:
    """Extract reference check outcome from transcript using Claude."""
    if not transcript or len(transcript.strip()) < 20:
        return {"outcome": "neutral", "summary": "No transcript", "confidence_score": 0.0, "recommends": False}

    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=EXTRACTION_MODEL,
            max_tokens=512,
            system=INTAKE_EXTRACTION_SYSTEM,
            messages=[{"role": "user", "content": f"{REFERENCE_EXTRACTION_SCHEMA}\n\nTranscript:\n{transcript}"}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3].strip()
        result = json.loads(raw)
        result.setdefault("confidence_score", 0.5)
        result.setdefault("outcome", "neutral")
        result.setdefault("recommends", False)
        return result

    except Exception as e:
        logger.error("Reference extraction failed: %s", e)
        return {"outcome": "neutral", "summary": f"Extraction error: {e}", "confidence_score": 0.0, "recommends": False}


# ---------- Background Jobs ----------

async def _fetch_vapi_transcript(vapi_call_id: str) -> dict:
    """Fetch call data from Vapi API."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{VAPI_BASE_URL}/call/{vapi_call_id}",
            headers={"Authorization": f"Bearer {settings.VAPI_API_KEY}"},
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json()


async def process_completed_intake_calls(db: AsyncSession) -> int:
    """Process completed intake calls: extract data and trigger reference calls."""
    stmt = (
        select(WorkerOnboardingCall)
        .where(
            WorkerOnboardingCall.call_type == OnboardingCallType.intake,
            WorkerOnboardingCall.status == AICallStatus.in_progress,
        )
    )
    calls = (await db.execute(stmt)).scalars().all()
    processed = 0

    for call in calls:
        try:
            if not call.vapi_call_id:
                continue

            vapi_data = await _fetch_vapi_transcript(call.vapi_call_id)
            vapi_status = vapi_data.get("status", "")

            if vapi_status in ("queued", "ringing", "in-progress"):
                continue

            if vapi_status != "ended":
                call.status = AICallStatus.failed
                call.ended_at = datetime.now(timezone.utc)
                processed += 1
                continue

            # Save transcript
            transcript = vapi_data.get("transcript", "")
            call.transcript = transcript
            call.ended_at = datetime.now(timezone.utc)
            call.status = AICallStatus.completed

            # Extract data
            worker = (await db.execute(
                select(Worker).where(Worker.id == call.worker_id)
            )).scalar_one()

            extraction = await extract_intake_data(transcript)
            await apply_intake_extraction(db, worker, extraction)

            # Trigger reference calls
            ref_stmt = select(WorkerReference).where(WorkerReference.worker_id == worker.id)
            references = (await db.execute(ref_stmt)).scalars().all()
            for ref in references:
                try:
                    await initiate_reference_call(db, worker, ref)
                except Exception as e:
                    logger.error("Failed to initiate reference call for %s: %s", ref.reference_name, e)

            processed += 1
            logger.info("Intake call processed for worker %s", worker.id)

        except Exception as e:
            logger.error("Failed to process intake call %s: %s", call.id, e)
            call.status = AICallStatus.failed
            call.ended_at = datetime.now(timezone.utc)

    await db.commit()
    return processed


async def process_completed_reference_calls(db: AsyncSession) -> int:
    """Process completed reference calls and finalize profiles when all refs are done."""
    stmt = (
        select(WorkerOnboardingCall)
        .where(
            WorkerOnboardingCall.call_type == OnboardingCallType.reference_check,
            WorkerOnboardingCall.status == AICallStatus.in_progress,
        )
    )
    calls = (await db.execute(stmt)).scalars().all()
    processed = 0

    for call in calls:
        try:
            if not call.vapi_call_id:
                continue

            vapi_data = await _fetch_vapi_transcript(call.vapi_call_id)
            vapi_status = vapi_data.get("status", "")

            if vapi_status in ("queued", "ringing", "in-progress"):
                continue

            if vapi_status != "ended":
                call.status = AICallStatus.failed
                call.ended_at = datetime.now(timezone.utc)
                # Mark related ReferenceCall as failed
                ref_calls = (await db.execute(
                    select(ReferenceCall).where(
                        ReferenceCall.worker_id == call.worker_id,
                        ReferenceCall.call_status == ReferenceCallStatus.pending,
                    )
                )).scalars().all()
                for rc in ref_calls:
                    rc.call_status = ReferenceCallStatus.failed
                processed += 1
                continue

            transcript = vapi_data.get("transcript", "")
            call.transcript = transcript
            call.ended_at = datetime.now(timezone.utc)
            call.status = AICallStatus.completed

            # Extract reference outcome
            outcome_data = await extract_reference_outcome(transcript)

            # Update ReferenceCall record — find the one matching this worker with pending status
            ref_call_stmt = (
                select(ReferenceCall)
                .where(
                    ReferenceCall.worker_id == call.worker_id,
                    ReferenceCall.call_status == ReferenceCallStatus.pending,
                )
                .order_by(ReferenceCall.created_at.desc())
                .limit(1)
            )
            ref_call = (await db.execute(ref_call_stmt)).scalar_one_or_none()
            if ref_call:
                outcome_str = outcome_data.get("outcome", "neutral")
                try:
                    ref_call.outcome = ReferenceOutcome(outcome_str)
                except ValueError:
                    ref_call.outcome = ReferenceOutcome.neutral
                ref_call.call_status = ReferenceCallStatus.completed
                ref_call.transcript = transcript
                ref_call.ai_summary = outcome_data.get("summary", "")
                ref_call.confidence_score = outcome_data.get("confidence_score", 0.0)

            # Check if all references for this worker are done
            worker = (await db.execute(
                select(Worker).where(Worker.id == call.worker_id)
            )).scalar_one()

            all_refs = (await db.execute(
                select(ReferenceCall).where(ReferenceCall.worker_id == worker.id)
            )).scalars().all()

            all_done = all(
                rc.call_status in (ReferenceCallStatus.completed, ReferenceCallStatus.failed)
                for rc in all_refs
            )

            if all_done and all_refs:
                await finalize_worker_profile(db, worker)

            processed += 1

        except Exception as e:
            logger.error("Failed to process reference call %s: %s", call.id, e)
            call.status = AICallStatus.failed
            call.ended_at = datetime.now(timezone.utc)

    await db.commit()
    return processed


# ---------- Finalize Profile ----------

async def finalize_worker_profile(db: AsyncSession, worker: Worker) -> None:
    """Calculate final score and approve or flag worker for review."""
    # Gather reference outcomes
    ref_calls = (await db.execute(
        select(ReferenceCall).where(
            ReferenceCall.worker_id == worker.id,
            ReferenceCall.call_status == ReferenceCallStatus.completed,
        )
    )).scalars().all()

    reference_outcomes = [rc.outcome.value for rc in ref_calls if rc.outcome]

    # Get intake extraction data from the latest completed intake call
    intake_stmt = (
        select(WorkerOnboardingCall)
        .where(
            WorkerOnboardingCall.worker_id == worker.id,
            WorkerOnboardingCall.call_type == OnboardingCallType.intake,
            WorkerOnboardingCall.status == AICallStatus.completed,
        )
        .order_by(WorkerOnboardingCall.created_at.desc())
        .limit(1)
    )
    intake_call = (await db.execute(intake_stmt)).scalar_one_or_none()

    # Build extraction dict for scoring
    extraction = {"confidence_score": 0.5, "dpi": worker.dpi}
    if intake_call and intake_call.transcript:
        # Re-extract for scoring is expensive, use profile initial_score
        profile = (await db.execute(
            select(WorkerProfile).where(WorkerProfile.worker_id == worker.id)
        )).scalar_one_or_none()
        if profile and profile.initial_score:
            extraction["confidence_score"] = float(profile.initial_score)

    score = calculate_profile_score(extraction, reference_outcomes)

    profile = (await db.execute(
        select(WorkerProfile).where(WorkerProfile.worker_id == worker.id)
    )).scalar_one_or_none()

    if score >= 0.6:
        worker.is_active = True
        worker.is_vetted = True
        worker.vetting_date = datetime.now(timezone.utc).date()
        if profile:
            profile.profile_status = ProfileStatus.active
            profile.initial_score = score

        await sms_service.send_sms(
            db, worker.phone,
            f"Bienvenido a CHAN-C {worker.full_name}. Tu perfil fue aprobado. Te avisamos cuando haya trabajo.",
            worker_id=worker.id,
        )
        logger.info("Worker %s approved with score %.2f", worker.id, score)
    else:
        if profile:
            profile.profile_status = ProfileStatus.pending_review
            profile.initial_score = score
        logger.info("Worker %s flagged for review with score %.2f", worker.id, score)
