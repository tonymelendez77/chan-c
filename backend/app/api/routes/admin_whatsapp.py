"""Admin endpoints for managing WhatsApp conversations."""
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.api.deps import get_db, require_admin
from app.models import Company, WhatsAppConversation, Worker, WorkerProfile
from app.models.enums import ProfileStatus
from app.schemas.auth import TokenData
from app.services import whatsapp as wa_service

router = APIRouter(prefix="/admin", tags=["admin-whatsapp"])


class ConversationListItem(BaseModel):
    id: UUID
    phone: str
    role: str | None
    state: str
    needs_human: bool
    worker_id: UUID | None
    company_id: UUID | None
    last_message_at: datetime
    name: str = ""

    model_config = {"from_attributes": True}


class ConversationDetail(ConversationListItem):
    data: dict
    created_at: datetime
    updated_at: datetime


class SendMessageRequest(BaseModel):
    phone: str
    message: str


@router.get("/conversations", response_model=list[ConversationListItem])
async def list_conversations(
    role: str | None = None,
    state: str | None = None,
    needs_human: bool | None = None,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """List all WhatsApp conversations with optional filters."""
    stmt = select(WhatsAppConversation).order_by(WhatsAppConversation.last_message_at.desc())
    if role is not None:
        stmt = stmt.where(WhatsAppConversation.role == role)
    if state is not None:
        stmt = stmt.where(WhatsAppConversation.state == state)
    if needs_human is not None:
        stmt = stmt.where(WhatsAppConversation.needs_human.is_(needs_human))

    convs = (await db.execute(stmt)).scalars().all()
    out: list[ConversationListItem] = []
    for c in convs:
        item = ConversationListItem.model_validate(c)
        d = c.data or {}
        item.name = d.get("full_name") or d.get("contact_name") or d.get("company_name") or ""
        out.append(item)
    return out


@router.get("/conversations/{phone}", response_model=ConversationDetail)
async def get_conversation(
    phone: str,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Get a single conversation by phone."""
    conv = (await db.execute(select(WhatsAppConversation).where(WhatsAppConversation.phone == phone))).scalar_one_or_none()
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    item = ConversationDetail.model_validate(conv)
    d = conv.data or {}
    item.name = d.get("full_name") or d.get("contact_name") or d.get("company_name") or ""
    return item


@router.post("/conversations/{phone}/reset")
async def reset_conversation(
    phone: str,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Reset a conversation to idle state — useful when someone gets stuck."""
    conv = (await db.execute(select(WhatsAppConversation).where(WhatsAppConversation.phone == phone))).scalar_one_or_none()
    if conv is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    conv.state = "idle"
    conv.data = {}
    flag_modified(conv, "data")
    conv.needs_human = False
    await db.commit()
    return {"detail": "Conversation reset to idle"}


@router.post("/conversations/{phone}/approve-worker")
async def approve_worker_via_conv(
    phone: str,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Approve a worker linked to a WhatsApp conversation, send welcome message."""
    conv = (await db.execute(select(WhatsAppConversation).where(WhatsAppConversation.phone == phone))).scalar_one_or_none()
    if conv is None or conv.worker_id is None:
        raise HTTPException(status_code=404, detail="No worker linked to this conversation")

    worker = (await db.execute(select(Worker).where(Worker.id == conv.worker_id))).scalar_one_or_none()
    if worker is None:
        raise HTTPException(status_code=404, detail="Worker not found")

    worker.is_active = True
    worker.is_vetted = True

    profile = (await db.execute(select(WorkerProfile).where(WorkerProfile.worker_id == worker.id))).scalar_one_or_none()
    if profile:
        profile.profile_status = ProfileStatus.active
        profile.verified_at = datetime.now(timezone.utc)

    conv.state = "worker_active"

    await wa_service.send_whatsapp(
        db, worker.phone,
        f"✅ ¡Bienvenido a CHAN-C {worker.full_name}!\n"
        "Tu perfil fue aprobado.\n\n"
        "Te avisamos cuando haya trabajo disponible para ti. 💪",
        worker_id=worker.id,
    )
    await db.commit()
    return {"detail": "Worker approved and notified via WhatsApp"}


@router.post("/conversations/{phone}/approve-company")
async def approve_company_via_conv(
    phone: str,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Approve a company linked to a WhatsApp conversation, send welcome message."""
    conv = (await db.execute(select(WhatsAppConversation).where(WhatsAppConversation.phone == phone))).scalar_one_or_none()
    if conv is None or conv.company_id is None:
        raise HTTPException(status_code=404, detail="No company linked to this conversation")

    company = (await db.execute(select(Company).where(Company.id == conv.company_id))).scalar_one_or_none()
    if company is None:
        raise HTTPException(status_code=404, detail="Company not found")

    company.is_verified = True
    conv.state = "company_active"

    await wa_service.send_whatsapp(
        db, company.phone,
        f"✅ ¡Bienvenido a CHAN-C {company.name}!\n\n"
        "Tu empresa fue aprobada.\n\n"
        "Ya puedes publicar trabajos.\n"
        "Escribe TRABAJO para empezar. 💼",
    )
    await db.commit()
    return {"detail": "Company approved and notified via WhatsApp"}


@router.post("/whatsapp/send")
async def admin_send_whatsapp(
    data: SendMessageRequest,
    db: AsyncSession = Depends(get_db),
    _admin: TokenData = Depends(require_admin),
):
    """Send a custom WhatsApp message to any number (admin manual jump-in)."""
    sid = await wa_service.send_whatsapp(db, data.phone, data.message)
    await db.commit()
    return {"detail": "Sent", "twilio_sid": sid}
