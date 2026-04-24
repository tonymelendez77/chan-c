import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models import (
    AICall,
    AIExtraction,
    Company,
    Counteroffer,
    Job,
    Match,
    Worker,
)
from app.models.enums import (
    AICallStatus,
    AICallType,
    CounterofferProposedBy,
    CounterofferStatus,
    ExtractionFinalStatus,
    MatchStatus,
    WorkerReply,
)
from app.services import extraction_service, vapi_service

logger = logging.getLogger(__name__)


def _call_type_for_reply(worker_reply: WorkerReply | None) -> AICallType:
    """Map worker reply to AI call type."""
    if worker_reply == WorkerReply.contra:
        return AICallType.counteroffer
    return AICallType.job_offer


def _call_type_str(ai_call_type: AICallType) -> str:
    """Map AICallType enum to the string expected by extraction service."""
    if ai_call_type == AICallType.counteroffer:
        return "counteroffer"
    return "confirmation"


async def _get_company_name(db: AsyncSession, job: Job) -> str:
    """Look up the company name for a job."""
    stmt = select(Company.name).where(Company.id == job.company_id)
    return (await db.execute(stmt)).scalar() or ""


async def process_pending_ai_calls(db: AsyncSession) -> int:
    """Find all matches with status pending_ai_call and initiate Vapi calls.

    Returns the count of calls initiated.
    """
    stmt = (
        select(Match)
        .where(Match.status == MatchStatus.pending_ai_call)
        .order_by(Match.created_at.asc())
    )
    matches = (await db.execute(stmt)).scalars().all()

    initiated = 0
    for match in matches:
        try:
            worker = (await db.execute(
                select(Worker).where(Worker.id == match.worker_id)
            )).scalar_one()

            if getattr(worker, "paused", False):
                logger.info("Skipping match %s — worker is paused", match.id)
                continue

            job = (await db.execute(
                select(Job).where(Job.id == match.job_id)
            )).scalar_one()

            company_name = await _get_company_name(db, job)
            call_type = _call_type_for_reply(match.worker_reply)

            # Create ai_call record
            ai_call = AICall(
                match_id=match.id,
                worker_id=worker.id,
                call_type=call_type,
                status=AICallStatus.initiated,
                started_at=datetime.now(timezone.utc),
            )
            db.add(ai_call)
            await db.flush()

            # Initiate Vapi call
            vapi_call_id = await vapi_service.initiate_call(match, worker, job, company_name)
            ai_call.vapi_call_id = vapi_call_id
            ai_call.status = AICallStatus.in_progress

            # Update match status
            match.status = MatchStatus.call_in_progress

            initiated += 1
            logger.info("Call initiated for match %s (type=%s)", match.id, call_type.value)

        except Exception as e:
            logger.error("Failed to initiate call for match %s: %s", match.id, e)
            # Flag for admin review instead of leaving in pending_ai_call forever
            match.status = MatchStatus.pending_review

    await db.commit()
    return initiated


async def process_completed_calls(db: AsyncSession) -> int:
    """Check all in-progress AI calls and process completed ones.

    Returns the count of calls processed.
    """
    stmt = (
        select(AICall)
        .where(AICall.status == AICallStatus.in_progress)
        .order_by(AICall.created_at.asc())
    )
    calls = (await db.execute(stmt)).scalars().all()

    processed = 0
    for ai_call in calls:
        try:
            # Fetch status from Vapi
            if not ai_call.vapi_call_id:
                logger.warning("AI call %s has no vapi_call_id, skipping", ai_call.id)
                continue

            vapi_data = await vapi_service.get_call_status(ai_call.vapi_call_id)
            vapi_status = vapi_data["status"]

            # Still in progress
            if vapi_status in ("queued", "ringing", "in-progress"):
                continue

            # Call ended — determine outcome
            if vapi_status == "ended":
                await _handle_completed_call(db, ai_call, vapi_data)
            else:
                # failed, no-answer, busy, etc.
                await _handle_failed_call(db, ai_call, vapi_status)

            processed += 1

        except Exception as e:
            logger.error("Failed to process AI call %s: %s", ai_call.id, e)
            # Don't change status — retry on next run

    await db.commit()
    return processed


async def _handle_completed_call(
    db: AsyncSession, ai_call: AICall, vapi_data: dict
) -> None:
    """Process a successfully completed Vapi call."""
    # Save transcript and recording
    ai_call.transcript = vapi_data.get("transcript", "")
    ai_call.duration_seconds = vapi_data.get("duration_seconds")
    ai_call.recording_url = vapi_data.get("recording_url", "")
    ai_call.ended_at = vapi_data.get("ended_at") or datetime.now(timezone.utc)
    ai_call.status = AICallStatus.completed

    call_type_str = _call_type_str(ai_call.call_type)

    # Extract structured data
    extraction_data = await extraction_service.extract_from_transcript(
        ai_call.transcript or "", call_type_str
    )

    # Map final_status string to enum
    final_status_str = extraction_data.get("final_status", "interested_with_conditions")
    try:
        final_status = ExtractionFinalStatus(final_status_str)
    except ValueError:
        final_status = ExtractionFinalStatus.interested_with_conditions

    confidence = float(extraction_data.get("confidence_score", 0.0))
    needs_review = extraction_data.get("requires_admin_review", confidence < settings.CONFIDENCE_THRESHOLD)

    # Save extraction
    extraction = AIExtraction(
        call_id=ai_call.id,
        can_cover=extraction_data.get("can_cover"),
        cannot_cover=extraction_data.get("cannot_cover"),
        counteroffer_price=extraction_data.get("proposed_rate"),
        counteroffer_dates=extraction_data.get("proposed_dates"),
        counteroffer_notes=extraction_data.get("counteroffer_notes"),
        availability_notes=extraction_data.get("availability_notes"),
        has_required_tools=extraction_data.get("has_required_tools"),
        tools_comment=extraction_data.get("tools_comment"),
        final_status=final_status,
        confidence_score=confidence,
        requires_admin_review=needs_review,
        extraction_model=extraction_service.EXTRACTION_MODEL,
    )
    db.add(extraction)
    await db.flush()

    # If counteroffer call, create a counteroffer record
    if ai_call.call_type == AICallType.counteroffer and ai_call.match_id:
        match = (await db.execute(
            select(Match).where(Match.id == ai_call.match_id)
        )).scalar_one_or_none()

        if match:
            job = (await db.execute(
                select(Job).where(Job.id == match.job_id)
            )).scalar_one()

            counteroffer = Counteroffer(
                match_id=match.id,
                proposed_by=CounterofferProposedBy.worker,
                original_rate=match.offered_rate,
                proposed_rate=extraction_data.get("proposed_rate"),
                original_start=job.start_date,
                original_end=job.end_date,
                notes=extraction_data.get("counteroffer_notes", ""),
                status=CounterofferStatus.pending,
            )
            db.add(counteroffer)

    # Update match status based on confidence
    if ai_call.match_id:
        match = (await db.execute(
            select(Match).where(Match.id == ai_call.match_id)
        )).scalar_one_or_none()

        if match:
            if confidence >= settings.CONFIDENCE_THRESHOLD:
                match.status = MatchStatus.pending_company_decision
                await notify_company(db, match, extraction_data, ai_call.call_type)
            else:
                match.status = MatchStatus.pending_review

    logger.info("Call %s completed: confidence=%.2f, review=%s",
                ai_call.id, confidence, needs_review)


async def _handle_failed_call(
    db: AsyncSession, ai_call: AICall, vapi_status: str
) -> None:
    """Handle a failed or unanswered Vapi call."""
    if vapi_status in ("no-answer", "busy"):
        ai_call.status = AICallStatus.no_answer
    else:
        ai_call.status = AICallStatus.failed

    ai_call.ended_at = datetime.now(timezone.utc)

    # Flag match for admin review
    if ai_call.match_id:
        match = (await db.execute(
            select(Match).where(Match.id == ai_call.match_id)
        )).scalar_one_or_none()
        if match:
            match.status = MatchStatus.pending_review

    logger.warning("Call %s ended with status: %s", ai_call.id, vapi_status)


async def notify_company(
    db: AsyncSession,
    match: Match,
    extraction_data: dict,
    call_type: AICallType,
) -> None:
    """Build a formatted summary for the company dashboard notification.

    For now, this stores the notification text. A real notification
    system (email/push/websocket) will be added later.
    """
    worker = (await db.execute(
        select(Worker).where(Worker.id == match.worker_id)
    )).scalar_one()

    if call_type == AICallType.counteroffer:
        proposed_rate = extraction_data.get("proposed_rate", "N/A")
        proposed_dates = extraction_data.get("proposed_dates", "N/A")
        counteroffer_notes = extraction_data.get("counteroffer_notes", "")
        summary = (
            f"{worker.full_name} propone una contrapropuesta:\n"
            f"Precio propuesto: Q{proposed_rate}/dia "
            f"(usted ofrecio Q{int(match.offered_rate)})\n"
            f"Fechas: {proposed_dates}\n"
            f"Condiciones: {counteroffer_notes}\n"
            f"Acepta, negocia o solicita otro trabajador?"
        )
    else:
        can_cover = ", ".join(extraction_data.get("can_cover", [])) or "N/A"
        cannot_cover = ", ".join(extraction_data.get("cannot_cover", [])) or "N/A"
        availability = extraction_data.get("availability_notes", "")
        summary = (
            f"{worker.full_name} esta interesado en su proyecto.\n"
            f"Puede cubrir: {can_cover}\n"
            f"No puede cubrir: {cannot_cover}\n"
            f"Notas: {availability}\n"
            f"Acepta, negocia o solicita otro trabajador?"
        )

    # TODO: Send via email/push/websocket when notification system is built
    logger.info("Company notification for match %s:\n%s", match.id, summary)
