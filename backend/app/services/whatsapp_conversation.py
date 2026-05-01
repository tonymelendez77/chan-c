"""WhatsApp conversation state machine — Phase 1 of CHAN-C.

This is the brain of the bot. handle_message() is the single entry point.
"""
import logging
import re
import uuid
from datetime import date, datetime, timezone
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.core.config import settings
from app.models import (
    Company,
    Job,
    Match,
    User,
    WhatsAppConversation,
    Worker,
    WorkerProfile,
    WorkerReference,
    WorkerTrade,
)
from app.models.enums import (
    CompanyType,
    JobStatus,
    Language,
    MatchStatus,
    ProfileStatus,
    SkillLevel,
    SkillLevelRequired,
    Trade,
    UserRole,
)
from app.services import whatsapp as wa_service
from app.services import whatsapp_parser as p
from app.core.security import hash_password

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════════════════
#  Helpers
# ════════════════════════════════════════════════════════════════════════

TRADE_LABELS_ES = {
    "electrician": "Electricista", "plumber": "Plomero", "mason": "Albañil",
    "carpenter": "Carpintero", "painter": "Pintor", "welder": "Soldador",
    "roofer": "Techador", "general_labor": "Ayudante general",
    "security": "Seguridad", "housemaid": "Limpieza", "gardener": "Jardinero",
    "other": "Otro",
}

TOOLS_FRIENDLY = {
    "own_tools": "Tiene sus herramientas",
    "partial_tools": "Tiene algunas herramientas",
    "needs_tools": "Necesita herramientas",
    "depends_on_job": "Depende del trabajo",
}

TRADE_MENU = (
    "1️⃣ Electricista\n"
    "2️⃣ Plomero\n"
    "3️⃣ Albañil\n"
    "4️⃣ Carpintero\n"
    "5️⃣ Pintor\n"
    "6️⃣ Soldador\n"
    "7️⃣ Techador\n"
    "8️⃣ Ayudante general\n"
    "9️⃣ Seguridad\n"
    "🔟 Limpieza\n"
    "1️⃣1️⃣ Jardinero\n"
    "✏️ Escribe tu oficio si no está en la lista"
)


async def get_or_create_conversation(db: AsyncSession, phone: str) -> WhatsAppConversation:
    stmt = select(WhatsAppConversation).where(WhatsAppConversation.phone == phone)
    conv = (await db.execute(stmt)).scalar_one_or_none()
    if conv is None:
        conv = WhatsAppConversation(phone=phone, state="idle", data={})
        db.add(conv)
        await db.flush()
    return conv


async def update_state(
    db: AsyncSession,
    conv: WhatsAppConversation,
    new_state: str,
    data_updates: dict | None = None,
) -> None:
    conv.state = new_state
    if data_updates:
        merged = dict(conv.data or {})
        merged.update(data_updates)
        conv.data = merged
        flag_modified(conv, "data")
    conv.last_message_at = datetime.now(timezone.utc)


async def _notify_cece(db: AsyncSession, message: str) -> None:
    """Send a notification to Cece's WhatsApp number."""
    if not settings.CECE_WHATSAPP_NUMBER:
        logger.warning("CECE_WHATSAPP_NUMBER not configured; skipping admin notification.")
        return
    try:
        await wa_service.send_whatsapp(db, settings.CECE_WHATSAPP_NUMBER, message)
    except Exception as e:
        logger.error("Failed to notify Cece: %s", e)


# ════════════════════════════════════════════════════════════════════════
#  Idle / Welcome
# ════════════════════════════════════════════════════════════════════════

WELCOME_MESSAGE = (
    "Hola 👋 Bienvenido a CHAN-C.\n\n"
    "Somos la plataforma que conecta empresas con los mejores trabajadores "
    "de construcción en Guatemala.\n\n"
    "¿Eres trabajador o empresa?\n\n"
    "1️⃣ Soy trabajador — escribe TRABAJAR\n"
    "2️⃣ Soy empresa — escribe HOLA\n\n"
    "¿Necesitas ayuda? Escribe AYUDA"
)


# ════════════════════════════════════════════════════════════════════════
#  Worker registration flow
# ════════════════════════════════════════════════════════════════════════

async def handle_worker_registration(
    db: AsyncSession, conv: WhatsAppConversation, message: str
) -> str:
    state = conv.state

    if state == "worker_ask_name":
        await update_state(db, conv, "worker_ask_trade", {"full_name": message.strip()})
        return f"Mucho gusto {message.strip()} 👋\n\n¿Cuál es tu oficio principal?\n\n{TRADE_MENU}"

    if state == "worker_ask_trade":
        trade = p.parse_trade(message)
        if not trade:
            return f"No entendí el oficio. Por favor escribe el número o nombre del oficio.\n\n{TRADE_MENU}"
        await update_state(db, conv, "worker_ask_experience", {"trade": trade})
        return f"¿Cuántos años de experiencia tienes como {TRADE_LABELS_ES[trade]}?"

    if state == "worker_ask_experience":
        years = p.parse_number(message)
        if years is None:
            return "Por favor escribe solo el número de años. Ejemplo: 5"
        await update_state(db, conv, "worker_ask_zones", {"years_experience": years})
        return (
            "¿En qué zonas de Guatemala City puedes trabajar?\n\n"
            "Escribe las zonas separadas por coma.\n"
            "Ejemplo: Zona 1, Zona 5, Zona 10\n\n"
            "O escribe TODAS si trabajas en cualquier zona."
        )

    if state == "worker_ask_zones":
        zones = p.parse_zones(message)
        if not zones:
            return "No entendí las zonas. Escribe ejemplo: Zona 1, Zona 5"
        await update_state(db, conv, "worker_ask_tools", {"preferred_zones": zones})
        return (
            "¿Tienes tus propias herramientas?\n\n"
            "1️⃣ Sí, tengo todas mis herramientas\n"
            "2️⃣ Tengo algunas herramientas\n"
            "3️⃣ No tengo herramientas\n"
            "4️⃣ Depende del trabajo"
        )

    if state == "worker_ask_tools":
        tools = p.parse_tools(message)
        if not tools:
            return "Por favor responde con el número 1, 2, 3 o 4."
        await update_state(db, conv, "worker_ask_rate", {"tools_status": tools})
        return (
            "¿Cuánto cobras por día de trabajo en quetzales?\n\n"
            "Escribe solo el número.\n"
            "Ejemplo: 350"
        )

    if state == "worker_ask_rate":
        rate = p.parse_rate(message)
        if rate is None or rate <= 0:
            return "Por favor escribe solo el número. Ejemplo: 350"
        await update_state(db, conv, "worker_ask_reference", {"daily_rate": str(rate)})
        return (
            "Ya casi terminamos 💪\n\n"
            "Dame el nombre y teléfono de alguien que pueda dar referencias de tu trabajo.\n\n"
            "Ejemplo: Juan López, 55551234"
        )

    if state == "worker_ask_reference":
        ref = p.parse_reference(message)
        if not ref:
            return "No entendí. Escribe nombre y teléfono. Ejemplo: Juan López, 55551234"

        ref_name, ref_phone = ref
        data = dict(conv.data or {})
        data["reference_name"] = ref_name
        data["reference_phone"] = ref_phone

        # ─── Create worker records ──────────────────────────────
        zones = data.get("preferred_zones") or []
        primary_zone = zones[0] if zones else ""
        # Strip "Zona " prefix to match how it's stored elsewhere
        primary_zone_stripped = re.sub(r"^Zona\s*", "", primary_zone, flags=re.I)

        worker = Worker(
            full_name=data["full_name"],
            phone=conv.phone,
            zone=primary_zone_stripped or "",
            language=Language.spanish,
            is_active=False,
            is_vetted=False,
            is_available=True,
        )
        db.add(worker)
        await db.flush()

        profile = WorkerProfile(
            worker_id=worker.id,
            profile_status=ProfileStatus.pending_review,
            bio=(
                f"Oficio: {TRADE_LABELS_ES[data['trade']]}. "
                f"Tarifa: Q{data['daily_rate']}/día. "
                f"Zonas: {', '.join(zones)}."
            ),
        )
        db.add(profile)

        try:
            trade_enum = Trade(data["trade"])
        except ValueError:
            trade_enum = Trade.other
        worker_trade = WorkerTrade(
            worker_id=worker.id,
            trade=trade_enum,
            skill_level=SkillLevel.mid,
            years_experience=int(data.get("years_experience", 0)),
            tools_status=data.get("tools_status"),
        )
        db.add(worker_trade)

        worker_ref = WorkerReference(
            worker_id=worker.id,
            reference_name=ref_name,
            reference_phone=ref_phone,
            relationship="laboral",
        )
        db.add(worker_ref)

        conv.worker_id = worker.id
        conv.role = "worker"
        await update_state(db, conv, "worker_pending_approval", data)

        # Notify Cece
        await _notify_cece(
            db,
            "🆕 Nuevo trabajador registrado\n\n"
            f"Nombre: {data['full_name']}\n"
            f"Oficio: {TRADE_LABELS_ES[data['trade']]}\n"
            f"Teléfono: {conv.phone}\n"
            f"Tarifa: Q{data['daily_rate']}/día\n"
            f"Herramientas: {TOOLS_FRIENDLY.get(data['tools_status'], data['tools_status'])}\n"
            f"Zonas: {', '.join(zones)}\n"
            f"Referencia: {ref_name} - {ref_phone}\n\n"
            "Revisa en: localhost:3000/admin/workers/pending",
        )

        return (
            f"✅ Listo {data['full_name']}.\n\n"
            "Recibimos tu solicitud para unirte a CHAN-C.\n\n"
            "Nuestro equipo revisará tu perfil y te llamará para verificar tus datos.\n\n"
            "Te avisamos por aquí cuando estés aprobado. ¡Gracias! 🙏"
        )

    return "No entendí tu mensaje. Escribe AYUDA para ver las opciones."


# ════════════════════════════════════════════════════════════════════════
#  Company registration flow
# ════════════════════════════════════════════════════════════════════════

async def handle_company_registration(
    db: AsyncSession, conv: WhatsAppConversation, message: str
) -> str:
    state = conv.state

    if state == "company_ask_name":
        await update_state(db, conv, "company_ask_contact", {"company_name": message.strip()})
        return "¿Cuál es tu nombre completo?"

    if state == "company_ask_contact":
        await update_state(db, conv, "company_ask_email", {"contact_name": message.strip()})
        return "¿Cuál es tu correo electrónico?"

    if state == "company_ask_email":
        email = message.strip().lower()
        if "@" not in email or "." not in email:
            return "Ese email no parece válido. Por favor escribe un correo. Ejemplo: contacto@empresa.gt"
        await update_state(db, conv, "company_ask_type", {"email": email})
        return (
            "¿Qué tipo de empresa es?\n\n"
            "1️⃣ Construcción\n"
            "2️⃣ Arquitectura\n"
            "3️⃣ Administración de propiedades\n"
            "4️⃣ Otro"
        )

    if state == "company_ask_type":
        ctype = p.parse_company_type(message)
        if not ctype:
            return "Por favor responde con un número del 1 al 4."
        await update_state(db, conv, "company_ask_zone", {"company_type": ctype})
        return "¿En qué zona de Guatemala City está tu empresa?"

    if state == "company_ask_zone":
        zones = p.parse_zones(message)
        zone = zones[0].replace("Zona ", "") if zones else message.strip()
        await update_state(db, conv, "company_ask_nit", {"zone": zone})
        return "¿Cuál es tu NIT?\n(Escribe NO si no tienes)"

    if state == "company_ask_nit":
        norm = p._normalize(message)
        nit = None if norm in {"no", "n", "no tengo"} else message.strip()

        data = dict(conv.data or {})
        data["tax_id"] = nit or ""

        # ─── Create user + company records ──────────────────────
        user = User(
            email=data["email"],
            password_hash=hash_password(uuid.uuid4().hex[:16]),  # temp password
            role=UserRole.company,
            is_active=False,
        )
        db.add(user)
        await db.flush()

        try:
            ctype_enum = CompanyType(data["company_type"])
        except ValueError:
            ctype_enum = CompanyType.other

        company = Company(
            user_id=user.id,
            name=data["company_name"],
            contact_name=data["contact_name"],
            phone=conv.phone,
            email=data["email"],
            zone=data.get("zone", ""),
            company_type=ctype_enum,
            tax_id=data.get("tax_id") or "",
            is_verified=False,
        )
        db.add(company)
        await db.flush()

        conv.company_id = company.id
        conv.role = "company"
        await update_state(db, conv, "company_pending_approval", data)

        await _notify_cece(
            db,
            "🏢 Nueva empresa registrada\n\n"
            f"Empresa: {data['company_name']}\n"
            f"Contacto: {data['contact_name']}\n"
            f"Email: {data['email']}\n"
            f"Tipo: {data['company_type']}\n"
            f"Zona: {data.get('zone', '')}\n"
            f"Teléfono: {conv.phone}\n\n"
            "Revisa en: localhost:3000/admin/companies/pending",
        )

        return (
            f"✅ Perfecto {data['contact_name']}.\n\n"
            f"Recibimos el registro de {data['company_name']}.\n\n"
            "Nuestro equipo revisará tu solicitud en las próximas horas.\n\n"
            "Te confirmamos por aquí cuando estés activo. ¡Gracias! 🙏"
        )

    return "No entendí tu mensaje. Escribe AYUDA para ver las opciones."


# ════════════════════════════════════════════════════════════════════════
#  Job posting flow
# ════════════════════════════════════════════════════════════════════════

async def handle_job_posting(
    db: AsyncSession, conv: WhatsAppConversation, message: str
) -> str:
    state = conv.state

    if state == "job_ask_trade":
        trade = p.parse_trade(message)
        if not trade:
            return f"No entendí el oficio.\n\n{TRADE_MENU}"
        await update_state(db, conv, "job_ask_zone", {"job_trade": trade})
        return "¿En qué zona de Guatemala City es el trabajo?"

    if state == "job_ask_zone":
        zones = p.parse_zones(message)
        zone = zones[0].replace("Zona ", "") if zones else message.strip()
        await update_state(db, conv, "job_ask_dates", {"job_zone": zone})
        return (
            "¿Cuándo necesitas al trabajador?\n\n"
            "Escribe fecha de inicio y fin.\n"
            "Ejemplo: 5 de mayo al 10 de mayo"
        )

    if state == "job_ask_dates":
        # Free-text dates — we store the raw string for Cece to confirm.
        await update_state(db, conv, "job_ask_rate", {"job_dates_raw": message.strip()})
        return "¿Cuánto pagas por día en quetzales?\nEjemplo: 350"

    if state == "job_ask_rate":
        rate = p.parse_rate(message)
        if rate is None or rate <= 0:
            return "Por favor escribe solo el número. Ejemplo: 350"
        await update_state(db, conv, "job_ask_tools", {"job_rate": str(rate)})
        return (
            "¿La empresa provee herramientas?\n\n"
            "1️⃣ Sí, la empresa provee todo\n"
            "2️⃣ No, el trabajador debe traer las suyas"
        )

    if state == "job_ask_tools":
        provided = p.parse_tools_provided(message)
        if provided is None:
            return "Por favor responde 1 (sí provee) o 2 (no provee)."
        await update_state(db, conv, "job_ask_headcount", {"job_tools_provided": provided})
        return "¿Cuántos trabajadores necesitas?"

    if state == "job_ask_headcount":
        n = p.parse_number(message)
        if n is None or n < 1:
            return "Por favor escribe un número. Ejemplo: 1"
        await update_state(db, conv, "job_ask_description", {"job_headcount": n})
        return (
            "¿Algún requisito especial?\n\n"
            "Escribe los detalles o LISTO si no hay requisitos adicionales."
        )

    if state == "job_ask_description":
        norm = p._normalize(message)
        description = "" if norm == "listo" else message.strip()
        data = dict(conv.data or {})
        data["job_description"] = description

        # ─── Create job ──────────────────────────────────────────
        if not conv.company_id:
            return "Error: tu empresa no está activa. Escribe AYUDA."

        # Default dates: today → today + 1 day if we cannot parse
        start_date, end_date = _parse_date_range(data.get("job_dates_raw", ""))

        try:
            trade_enum = Trade(data["job_trade"])
        except ValueError:
            trade_enum = Trade.other

        job = Job(
            company_id=conv.company_id,
            title=f"{TRADE_LABELS_ES[data['job_trade']]} en Zona {data['job_zone']}",
            trade_required=trade_enum,
            skill_level_required=SkillLevelRequired.any,
            zone=data["job_zone"],
            start_date=start_date,
            end_date=end_date,
            daily_rate=Decimal(data["job_rate"]),
            currency="GTQ",
            headcount=int(data["job_headcount"]),
            description=description or "Sin requisitos especiales adicionales.",
            tools_provided=bool(data.get("job_tools_provided", False)),
            status=JobStatus.open,
            created_by=conv.company_id,  # placeholder; real user_id from company.user_id
        )

        # Set created_by to the company's user_id
        company = (await db.execute(select(Company).where(Company.id == conv.company_id))).scalar_one_or_none()
        if company:
            job.created_by = company.user_id
            company_name = company.name
        else:
            company_name = "Empresa"

        db.add(job)
        await db.flush()

        # Reset to active state, clear job-related data
        clean_data = {k: v for k, v in (conv.data or {}).items() if not k.startswith("job_")}
        await update_state(db, conv, "company_active", clean_data)

        # Reload to clear job_ keys
        conv.data = clean_data
        flag_modified(conv, "data")

        await _notify_cece(
            db,
            "📋 Nuevo trabajo publicado\n\n"
            f"Empresa: {company_name}\n"
            f"Oficio: {TRADE_LABELS_ES[data['job_trade']]}\n"
            f"Zona: {data['job_zone']}\n"
            f"Fechas: {data.get('job_dates_raw', '')}\n"
            f"Tarifa: Q{data['job_rate']}/día\n"
            f"Trabajadores: {data['job_headcount']}\n"
            f"Herramientas: {'La empresa provee' if data.get('job_tools_provided') else 'Trabajador trae las suyas'}\n\n"
            "Revisa en: localhost:3000/admin/jobs",
        )

        return (
            "✅ Trabajo publicado.\n\n"
            "Estamos buscando al trabajador ideal para ti.\n\n"
            "Te avisamos cuando tengamos un match 💪"
        )

    return "No entendí tu mensaje. Escribe AYUDA."


def _parse_date_range(text: str) -> tuple[date, date]:
    """Best-effort parse of '5 de mayo al 10 de mayo' or similar."""
    today = date.today()
    nums = re.findall(r"\d+", text)
    months = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
        "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
        "noviembre": 11, "diciembre": 12,
    }
    found_month = None
    norm = text.lower()
    for name, m in months.items():
        if name in norm:
            found_month = m
            break
    year = today.year
    try:
        if len(nums) >= 2 and found_month:
            return (date(year, found_month, int(nums[0])), date(year, found_month, int(nums[1])))
    except (ValueError, OverflowError):
        pass
    # Fallback: today through today+1
    from datetime import timedelta
    return (today, today + timedelta(days=1))


# ════════════════════════════════════════════════════════════════════════
#  Status / matches / help / human handoff
# ════════════════════════════════════════════════════════════════════════

async def handle_status_check(db: AsyncSession, conv: WhatsAppConversation) -> str:
    if not conv.company_id:
        return "No tienes empresa registrada. Escribe HOLA para registrarte."

    stmt = select(Job).where(Job.company_id == conv.company_id, Job.status != JobStatus.cancelled).order_by(Job.created_at.desc())
    jobs = (await db.execute(stmt)).scalars().all()

    if not jobs:
        return "No tienes trabajos activos.\nEscribe TRABAJO para publicar uno."

    lines = ["📊 Tus trabajos activos:\n"]
    for i, job in enumerate(jobs[:10], 1):
        status_icon = {
            JobStatus.open: "🔍 Buscando trabajador",
            JobStatus.matching: "🔍 Buscando trabajador",
            JobStatus.filled: "✅ Match encontrado — esperando tu decisión",
            JobStatus.completed: "✔️ Completado",
            JobStatus.draft: "📝 Borrador",
            JobStatus.cancelled: "❌ Cancelado",
        }.get(job.status, str(job.status.value))
        lines.append(f"{i}. {TRADE_LABELS_ES.get(job.trade_required.value, str(job.trade_required.value))} - Zona {job.zone}")
        lines.append(f"   Estado: {status_icon}\n")

    lines.append("Escribe MATCHES para ver los matches pendientes.")
    return "\n".join(lines)


async def handle_matches_check(db: AsyncSession, conv: WhatsAppConversation) -> str:
    if not conv.company_id:
        return "No tienes empresa registrada. Escribe HOLA para registrarte."

    stmt = (
        select(Match, Worker, Job)
        .join(Worker, Match.worker_id == Worker.id)
        .join(Job, Match.job_id == Job.id)
        .where(Job.company_id == conv.company_id, Match.status == MatchStatus.pending_company_decision)
        .order_by(Match.created_at.desc())
    )
    rows = (await db.execute(stmt)).all()

    if not rows:
        return "No tienes matches pendientes en este momento.\nTe avisaremos cuando tengamos uno 💪"

    out = ["📋 Matches pendientes:\n"]
    for i, (match, worker, job) in enumerate(rows[:5], 1):
        # Get tools_status from worker's primary trade
        trade_stmt = select(WorkerTrade).where(WorkerTrade.worker_id == worker.id).limit(1)
        wtrade = (await db.execute(trade_stmt)).scalar_one_or_none()
        tools_text = TOOLS_FRIENDLY.get(wtrade.tools_status, "—") if wtrade else "—"

        # First name + last initial
        parts = worker.full_name.split()
        display_name = parts[0] + (f" {parts[-1][0]}." if len(parts) > 1 else "")

        out.append(f"{i}. 👷 {display_name}")
        out.append(f"   ⭐ {worker.rating_avg:.1f} · {worker.total_jobs} trabajos")
        out.append(f"   🔧 {tools_text}")
        out.append(f"   💰 Q{int(match.offered_rate)}/día")
        out.append(f"   📌 {TRADE_LABELS_ES.get(job.trade_required.value, str(job.trade_required.value))} - Zona {job.zone}\n")

    out.append("Escribe ACEPTAR [número] para aceptar")
    out.append("Escribe OTRO [número] para pedir otro")
    return "\n".join(out)


HELP_MESSAGE_COMPANY = (
    "🆘 *Comandos disponibles:*\n\n"
    "TRABAJO → Publicar nuevo trabajo\n"
    "ESTADO → Ver tus trabajos activos\n"
    "MATCHES → Ver matches pendientes\n"
    "AYUDA → Ver este menú\n\n"
    "¿Necesitas ayuda personalizada?\n"
    "Escribe HUMANO y te conectamos con nuestro equipo."
)

HELP_MESSAGE_WORKER = (
    "🆘 *Comandos disponibles:*\n\n"
    "PAUSAR → Pausar ofertas\n"
    "REANUDAR → Reactivar ofertas\n"
    "AYUDA → Ver este menú\n\n"
    "¿Necesitas ayuda personalizada?\n"
    "Escribe HUMANO y te conectamos con nuestro equipo."
)


def handle_help(conv: WhatsAppConversation) -> str:
    if conv.role == "company":
        return HELP_MESSAGE_COMPANY
    return HELP_MESSAGE_WORKER


async def handle_human_handoff(db: AsyncSession, conv: WhatsAppConversation) -> str:
    conv.needs_human = True
    name = (conv.data or {}).get("full_name") or (conv.data or {}).get("contact_name") or "?"
    await _notify_cece(
        db,
        f"🙋 {conv.phone} necesita ayuda humana.\nRol: {conv.role or 'desconocido'}\nNombre: {name}",
    )
    return "Un momento 🙏\nTe conectamos con nuestro equipo.\nTe respondemos muy pronto."


# ════════════════════════════════════════════════════════════════════════
#  Match decision (ACEPTAR / OTRO)
# ════════════════════════════════════════════════════════════════════════

async def handle_match_decision(
    db: AsyncSession, conv: WhatsAppConversation, message: str
) -> str:
    """Handle ACEPTAR / OTRO from company in company_pending_match_decision state."""
    match_id_str = (conv.data or {}).get("pending_match_id")
    if not match_id_str:
        await update_state(db, conv, "company_active", {})
        return "No hay un match pendiente. Escribe ESTADO para ver tus trabajos."

    match = (await db.execute(select(Match).where(Match.id == uuid.UUID(match_id_str)))).scalar_one_or_none()
    if match is None:
        await update_state(db, conv, "company_active", {})
        return "No encontramos el match. Escribe MATCHES para ver pendientes."

    if p.is_accept_keyword(message):
        return await _accept_match(db, conv, match)
    if p.is_other_keyword(message):
        return await _reject_match(db, conv, match)

    return (
        "Para responder al match, escribe:\n"
        "• ACEPTAR para contratar al trabajador\n"
        "• OTRO para pedir otro trabajador"
    )


async def _accept_match(db: AsyncSession, conv: WhatsAppConversation, match: Match) -> str:
    from app.api.routes.matches import calculate_commission
    from app.models.enums import PaymentStatus, PaymentType
    from app.models import Payment

    job = (await db.execute(select(Job).where(Job.id == match.job_id))).scalar_one()
    worker = (await db.execute(select(Worker).where(Worker.id == match.worker_id))).scalar_one()
    company = (await db.execute(select(Company).where(Company.id == job.company_id))).scalar_one()

    match.status = MatchStatus.accepted
    match.company_decided_at = datetime.now(timezone.utc)

    job_value, commission_amount, _ = calculate_commission(job, match)
    payment = Payment(
        match_id=match.id,
        company_id=job.company_id,
        amount=commission_amount,
        job_value=job_value,
        commission_pct=Decimal("10.0"),
        currency=job.currency or "GTQ",
        payment_type=PaymentType.commission,
        status=PaymentStatus.pending,
        invoice_date=date.today(),
    )
    db.add(payment)
    job.total_value = job_value

    # Reset state and clear pending match
    clean_data = {k: v for k, v in (conv.data or {}).items() if k != "pending_match_id"}
    await update_state(db, conv, "company_active", clean_data)
    conv.data = clean_data
    flag_modified(conv, "data")

    # Notify worker
    try:
        await wa_service.send_whatsapp(
            db, worker.phone,
            "✅ *¡Tienes trabajo!*\n\n"
            f"{company.name} aceptó tu perfil para trabajo de "
            f"{TRADE_LABELS_ES.get(job.trade_required.value, str(job.trade_required.value))} en Zona {job.zone}.\n\n"
            f"📱 Contacto de la empresa: {company.phone}\n\n"
            "Por favor confírmales tu llegada.\n¡Mucho éxito! 💪",
            worker_id=worker.id,
        )
    except Exception as e:
        logger.error("Failed to notify worker of accepted match: %s", e)

    # Notify Cece
    await _notify_cece(
        db,
        f"✅ Match aceptado\n"
        f"{company.name} contrató a {worker.full_name}\n"
        f"Trabajo: {TRADE_LABELS_ES.get(job.trade_required.value, str(job.trade_required.value))} Zona {job.zone}\n"
        f"Comisión: Q{commission_amount}",
    )

    return (
        "✅ *¡Match confirmado!*\n\n"
        "Aquí está el contacto de tu trabajador:\n\n"
        f"👷 {worker.full_name}\n"
        f"📱 {worker.phone}\n\n"
        "Por favor coordina directamente con él.\n\n"
        "Recuerda: comisión del 10% sobre el valor total del trabajo.\n"
        "¡Mucho éxito! 🏗️"
    )


async def _reject_match(db: AsyncSession, conv: WhatsAppConversation, match: Match) -> str:
    job = (await db.execute(select(Job).where(Job.id == match.job_id))).scalar_one()
    worker = (await db.execute(select(Worker).where(Worker.id == match.worker_id))).scalar_one()
    company = (await db.execute(select(Company).where(Company.id == job.company_id))).scalar_one()

    match.status = MatchStatus.rejected_company
    match.company_decided_at = datetime.now(timezone.utc)

    clean_data = {k: v for k, v in (conv.data or {}).items() if k != "pending_match_id"}
    await update_state(db, conv, "company_active", clean_data)
    conv.data = clean_data
    flag_modified(conv, "data")

    await _notify_cece(
        db,
        f"❌ {company.name} rechazó a {worker.full_name}\n"
        f"para trabajo de {TRADE_LABELS_ES.get(job.trade_required.value, str(job.trade_required.value))} Zona {job.zone}\n"
        "Buscar otro trabajador.",
    )

    return "Entendido. Buscaremos otro trabajador para ti. Te avisamos pronto 🔍"


# ════════════════════════════════════════════════════════════════════════
#  Worker active flow (PAUSAR / REANUDAR)
# ════════════════════════════════════════════════════════════════════════

async def handle_worker_active(
    db: AsyncSession, conv: WhatsAppConversation, message: str
) -> str:
    if p.is_pausar_keyword(message):
        if conv.worker_id:
            worker = (await db.execute(select(Worker).where(Worker.id == conv.worker_id))).scalar_one_or_none()
            if worker:
                worker.paused = True
                worker.is_available = False
        await update_state(db, conv, "worker_paused", {})
        return (
            "⏸️ *Ofertas pausadas*\n"
            "Pausamos tus ofertas. Escribe *REANUDAR* cuando estés listo."
        )

    if p.is_help_keyword(message):
        return HELP_MESSAGE_WORKER

    if p.is_human_keyword(message):
        return await handle_human_handoff(db, conv)

    return (
        "Hola 👋 Tu perfil está activo.\n\n"
        "Te avisamos por aquí cuando haya un trabajo disponible.\n\n"
        "Escribe AYUDA para ver opciones."
    )


async def handle_worker_paused(
    db: AsyncSession, conv: WhatsAppConversation, message: str
) -> str:
    if p.is_reanudar_keyword(message):
        if conv.worker_id:
            worker = (await db.execute(select(Worker).where(Worker.id == conv.worker_id))).scalar_one_or_none()
            if worker:
                worker.paused = False
                worker.is_available = True
                worker.paused_until = None
        await update_state(db, conv, "worker_active", {})
        return (
            "▶️ *Ofertas reactivadas*\n"
            "Bienvenido de vuelta. Te avisamos cuando haya trabajo. 💪"
        )

    return "Tienes las ofertas pausadas. Escribe *REANUDAR* cuando estés disponible."


# ════════════════════════════════════════════════════════════════════════
#  Company active flow
# ════════════════════════════════════════════════════════════════════════

async def handle_company_active(
    db: AsyncSession, conv: WhatsAppConversation, message: str
) -> str:
    if p.is_job_post_keyword(message):
        await update_state(db, conv, "job_ask_trade", {})
        return f"Vamos a publicar tu trabajo 💼\n\n¿Qué oficio necesitas?\n\n{TRADE_MENU}"

    if p.is_status_keyword(message):
        return await handle_status_check(db, conv)

    if p.is_matches_keyword(message):
        return await handle_matches_check(db, conv)

    if p.is_help_keyword(message):
        return HELP_MESSAGE_COMPANY

    if p.is_human_keyword(message):
        return await handle_human_handoff(db, conv)

    return HELP_MESSAGE_COMPANY


# ════════════════════════════════════════════════════════════════════════
#  Main dispatcher
# ════════════════════════════════════════════════════════════════════════

async def handle_message(
    db: AsyncSession,
    phone: str,
    message: str,
    whatsapp_name: str = "",
) -> str:
    conv = await get_or_create_conversation(db, phone)
    state = conv.state

    # Global keywords always available
    if p.is_human_keyword(message):
        return await handle_human_handoff(db, conv)

    if p.is_help_keyword(message):
        return handle_help(conv)

    # Worker registration in progress
    if state.startswith("worker_ask_") or state == "worker_pending_approval":
        if state == "worker_pending_approval":
            return "Tu perfil está en revisión. Te avisamos pronto cuando seas aprobado 🙏"
        return await handle_worker_registration(db, conv, message)

    # Company registration in progress
    if state.startswith("company_ask_") or state == "company_pending_approval":
        if state == "company_pending_approval":
            return "Tu empresa está en revisión. Te avisamos pronto cuando seas aprobado 🙏"
        return await handle_company_registration(db, conv, message)

    # Job posting in progress
    if state.startswith("job_ask_"):
        return await handle_job_posting(db, conv, message)

    # Match decision pending
    if state == "company_pending_match_decision":
        return await handle_match_decision(db, conv, message)

    # Active worker
    if state == "worker_active":
        return await handle_worker_active(db, conv, message)

    if state == "worker_paused":
        return await handle_worker_paused(db, conv, message)

    # Active company
    if state == "company_active":
        return await handle_company_active(db, conv, message)

    # Idle — initial entry
    if state == "idle":
        if p.is_trabajar_keyword(message):
            await update_state(db, conv, "worker_ask_name", {})
            return "¡Genial! Vamos a registrarte 💪\n\n¿Cuál es tu nombre completo?"
        if p.is_company_intro_keyword(message):
            await update_state(db, conv, "company_ask_name", {})
            return "¡Bienvenido! 👋 Vamos a registrar tu empresa.\n\n¿Cuál es el nombre de tu empresa?"
        return WELCOME_MESSAGE

    return WELCOME_MESSAGE
