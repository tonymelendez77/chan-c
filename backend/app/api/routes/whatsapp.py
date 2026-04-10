from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from app.api.deps import get_db, require_admin
from app.core.config import settings
from app.models import Company, Job, Match, Worker, WorkerOnboardingCall, WorkerProfile
from app.models.enums import AICallStatus, MatchStatus, OnboardingCallType, ProfileStatus, WorkerReply
from app.models.enums import Language
from app.schemas.auth import TokenData
from app.schemas.sms import SendOfferRequest, SendTestRequest
from app.services import whatsapp as wa_service
from app.services.sms_parser import parse_worker_reply

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])

_PENDING_WORKER_STATUSES = [MatchStatus.pending_worker]


def _validate_twilio_signature(request: Request, form_body: dict) -> bool:
    """Verify the request really came from Twilio."""
    if not settings.TWILIO_WEBHOOK_SECRET:
        return True
    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    signature = request.headers.get("X-Twilio-Signature", "")
    url = str(request.url)
    return validator.validate(url, form_body, signature)


@router.post("/incoming")
async def incoming_whatsapp(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Twilio WhatsApp webhook — receives incoming messages from workers. Same logic as SMS."""
    twiml = MessagingResponse()

    form_data = {"From": From, "Body": Body}
    if MessageSid:
        form_data["MessageSid"] = MessageSid
    if not _validate_twilio_signature(request, form_data):
        return Response(content=str(twiml), media_type="text/xml", status_code=403)

    # Strip whatsapp: prefix and +502 to get 8-digit phone
    phone = From.replace("whatsapp:", "").replace("+502", "").replace("+", "").strip()

    # Look up worker by phone
    stmt = select(Worker).where(Worker.phone == phone)
    result = await db.execute(stmt)
    worker = result.scalar_one_or_none()

    reply = parse_worker_reply(Body)

    # --- TRABAJAR flow ---
    if reply == "TRABAJAR":
        await wa_service.log_inbound_whatsapp(
            db,
            worker_id=worker.id if worker else None,
            match_id=None,
            message=Body,
            twilio_sid=MessageSid,
        )

        if worker is not None and worker.is_active:
            await wa_service.send_whatsapp(
                db, worker.phone,
                "Ya tienes un perfil activo en CHAN-C. Te contactamos cuando haya trabajo para ti.",
                worker_id=worker.id,
            )
        elif worker is not None:
            await wa_service.send_whatsapp(
                db, worker.phone,
                "Tu perfil esta en revision. Te avisamos pronto.",
                worker_id=worker.id,
            )
        else:
            worker = Worker(
                phone=phone,
                full_name="Pendiente",
                zone="",
                language=Language.spanish,
                is_active=False,
                is_vetted=False,
            )
            db.add(worker)
            await db.flush()

            profile = WorkerProfile(
                worker_id=worker.id,
                profile_status=ProfileStatus.pending_review,
            )
            db.add(profile)

            onboarding_call = WorkerOnboardingCall(
                worker_id=worker.id,
                call_type=OnboardingCallType.intake,
                status=AICallStatus.initiated,
            )
            db.add(onboarding_call)

            await wa_service.send_whatsapp_intake_notice(db, worker)

        await db.commit()
        return Response(content=str(twiml), media_type="text/xml")

    # --- Existing flow ---
    if worker is None:
        twiml.message("No encontramos tu numero. Escribe TRABAJO para registrarte.")
        await wa_service.log_inbound_whatsapp(
            db, worker_id=None, match_id=None, message=Body, twilio_sid=MessageSid
        )
        await db.commit()
        return Response(content=str(twiml), media_type="text/xml")

    match_stmt = (
        select(Match)
        .where(Match.worker_id == worker.id, Match.status.in_(_PENDING_WORKER_STATUSES))
        .order_by(Match.created_at.desc())
        .limit(1)
    )
    match = (await db.execute(match_stmt)).scalar_one_or_none()

    await wa_service.log_inbound_whatsapp(
        db,
        worker_id=worker.id,
        match_id=match.id if match else None,
        message=Body,
        twilio_sid=MessageSid,
    )

    if match is None:
        twiml.message("No tienes ofertas pendientes en este momento.")
        await db.commit()
        return Response(content=str(twiml), media_type="text/xml")

    if reply == "SI":
        match.status = MatchStatus.pending_ai_call
        match.worker_reply = WorkerReply.yes
        match.worker_replied_at = datetime.now(timezone.utc)
        await wa_service.send_whatsapp(
            db, worker.phone,
            "Gracias. Te llamamos pronto para confirmar detalles.",
            worker_id=worker.id, match_id=match.id,
        )

    elif reply == "NO":
        match.status = MatchStatus.rejected_worker
        match.worker_reply = WorkerReply.no
        match.worker_replied_at = datetime.now(timezone.utc)
        await wa_service.send_whatsapp_job_declined(db, worker)

    elif reply == "CONTRA":
        match.status = MatchStatus.pending_ai_call
        match.worker_reply = WorkerReply.contra
        match.worker_replied_at = datetime.now(timezone.utc)
        await wa_service.send_whatsapp_counteroffer_call_notice(db, worker)

    else:
        await wa_service.send_whatsapp(
            db, worker.phone,
            "No entendimos tu respuesta. Responde *SI*, *NO* o *CONTRA*.",
            worker_id=worker.id, match_id=match.id,
        )

    await db.commit()
    return Response(content=str(twiml), media_type="text/xml")


@router.post("/send-offer", status_code=200)
async def send_whatsapp_offer(
    data: SendOfferRequest,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Admin endpoint — send WhatsApp job offer to matched worker and update match status."""
    match = (await db.execute(select(Match).where(Match.id == data.match_id))).scalar_one_or_none()
    if match is None:
        raise HTTPException(status_code=404, detail="Match not found")

    worker = (await db.execute(select(Worker).where(Worker.id == match.worker_id))).scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")

    job = (await db.execute(select(Job).where(Job.id == match.job_id))).scalar_one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    sid = await wa_service.send_whatsapp_job_offer(db, worker, match, job)

    match.status = MatchStatus.pending_worker
    match.worker_sms_sent_at = datetime.now(timezone.utc)

    await db.commit()
    return {"detail": "WhatsApp job offer sent", "twilio_sid": sid}


@router.post("/send-test", status_code=200)
async def send_whatsapp_test(
    data: SendTestRequest,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Admin endpoint — send a test WhatsApp to any phone number."""
    sid = await wa_service.send_whatsapp(db, data.phone, data.message)
    await db.commit()
    return {"detail": "Test WhatsApp sent", "twilio_sid": sid}
