"""WhatsApp webhook + admin endpoints — Phase 1 conversation engine.

Incoming messages are routed to the state-machine in
app.services.whatsapp_conversation. Replies are sent via Twilio WhatsApp.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from app.api.deps import get_db, require_admin
from app.core.config import settings
from app.models import Job, Match, Worker
from app.models.enums import MatchStatus
from app.schemas.auth import TokenData
from app.schemas.sms import SendOfferRequest, SendTestRequest
from app.services import whatsapp as wa_service
from app.services.whatsapp_conversation import (
    get_or_create_conversation,
    handle_message,
)

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


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
    ProfileName: str = Form(""),
    MessageSid: str = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Twilio WhatsApp webhook — routes every message through the conversation state machine."""
    twiml = MessagingResponse()

    form_data = {"From": From, "Body": Body}
    if ProfileName:
        form_data["ProfileName"] = ProfileName
    if MessageSid:
        form_data["MessageSid"] = MessageSid
    if not _validate_twilio_signature(request, form_data):
        return Response(content=str(twiml), media_type="text/xml", status_code=403)

    phone = (
        From.replace("whatsapp:", "")
        .replace("+502", "")
        .replace("+", "")
        .strip()
    )
    message = Body.strip()

    conv = await get_or_create_conversation(db, phone)
    await wa_service.log_inbound_whatsapp(
        db,
        worker_id=conv.worker_id,
        match_id=None,
        message=message,
        twilio_sid=MessageSid,
    )

    response_text = await handle_message(db, phone, message, ProfileName)

    try:
        await wa_service.send_whatsapp(
            db, to_phone=phone, message=response_text, worker_id=conv.worker_id,
        )
    except Exception:
        # Twilio sandbox/auth issue during dev — fall back to TwiML inline reply
        twiml.message(response_text)

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
