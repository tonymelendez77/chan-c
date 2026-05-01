"""Input parsing helpers for WhatsApp conversation engine.

Each parser is forgiving: handles digits, written keywords, accents, mixed case.
Returns None when the message cannot be confidently mapped.
"""
import re
import unicodedata
from decimal import Decimal, InvalidOperation


def _normalize(s: str) -> str:
    s = s.strip()
    s = unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode("ascii")
    return s.lower().strip()


# ─── Trade ─────────────────────────────────────────────────────────────

_TRADE_BY_NUMBER = {
    "1": "electrician", "2": "plumber", "3": "mason", "4": "carpenter",
    "5": "painter", "6": "welder", "7": "roofer", "8": "general_labor",
    "9": "security", "10": "housemaid", "11": "gardener",
}

_TRADE_KEYWORDS = {
    "electrician": ["electricista", "electrico", "electricidad"],
    "plumber": ["plomero", "plomeria", "fontanero"],
    "mason": ["albanil", "albanileria", "mason"],
    "carpenter": ["carpintero", "carpinteria"],
    "painter": ["pintor", "pintura"],
    "welder": ["soldador", "soldadura"],
    "roofer": ["techador", "techos", "techero"],
    "general_labor": ["ayudante", "general", "peon", "labor"],
    "security": ["seguridad", "guardian", "vigilante"],
    "housemaid": ["limpieza", "domestica", "muchacha"],
    "gardener": ["jardinero", "jardineria"],
    "other": ["otro", "otra"],
}


def parse_trade(message: str) -> str | None:
    norm = _normalize(message)
    digits = re.sub(r"[^\d]", "", norm)
    if digits in _TRADE_BY_NUMBER:
        return _TRADE_BY_NUMBER[digits]
    for trade, words in _TRADE_KEYWORDS.items():
        if any(w in norm for w in words):
            return trade
    return None


# ─── Tools ─────────────────────────────────────────────────────────────

_TOOLS_BY_NUMBER = {
    "1": "own_tools", "2": "partial_tools",
    "3": "needs_tools", "4": "depends_on_job",
}


def parse_tools(message: str) -> str | None:
    norm = _normalize(message)
    digits = re.sub(r"[^\d]", "", norm)
    if digits in _TOOLS_BY_NUMBER:
        return _TOOLS_BY_NUMBER[digits]
    if "todas" in norm or "tengo todas" in norm or norm in {"si", "sí"}:
        return "own_tools"
    if "algunas" in norm or "parcial" in norm:
        return "partial_tools"
    if "no tengo" in norm or "ninguna" in norm or norm == "no":
        return "needs_tools"
    if "depende" in norm:
        return "depends_on_job"
    return None


# ─── Company type ──────────────────────────────────────────────────────

_COMPANY_BY_NUMBER = {
    "1": "construction", "2": "architecture",
    "3": "property_management", "4": "other",
}


def parse_company_type(message: str) -> str | None:
    norm = _normalize(message)
    digits = re.sub(r"[^\d]", "", norm)
    if digits in _COMPANY_BY_NUMBER:
        return _COMPANY_BY_NUMBER[digits]
    if "construc" in norm:
        return "construction"
    if "arquitectur" in norm or "arquitec" in norm:
        return "architecture"
    if "propied" in norm or "administr" in norm or "inmobil" in norm:
        return "property_management"
    if "otro" in norm or "otra" in norm:
        return "other"
    return None


# ─── Tools-provided yes/no ─────────────────────────────────────────────

def parse_tools_provided(message: str) -> bool | None:
    norm = _normalize(message)
    digits = re.sub(r"[^\d]", "", norm)
    if digits == "1":
        return True
    if digits == "2":
        return False
    if "provee" in norm or "incluid" in norm or norm in {"si", "sí"}:
        return True
    if "trae" in norm or norm == "no":
        return False
    return None


# ─── Zones ─────────────────────────────────────────────────────────────

def parse_zones(message: str) -> list[str]:
    norm = _normalize(message)
    if "todas" in norm or norm == "todas":
        return [f"Zona {i}" for i in range(1, 26)]
    parts = re.split(r"[,;y]+|\sy\s", norm)
    out: list[str] = []
    for part in parts:
        digits = re.findall(r"\d+", part)
        if digits:
            out.append(f"Zona {digits[0]}")
        elif part.strip():
            out.append(part.strip().title())
    return out


# ─── Reference ─────────────────────────────────────────────────────────

def parse_reference(message: str) -> tuple[str, str] | None:
    """Parse 'Juan López, 55551234' or 'Juan Lopez 55551234' → (name, phone)."""
    s = message.strip()
    digits = re.findall(r"\d+", s)
    if not digits:
        return None
    phone = "".join(digits)[-8:] if len("".join(digits)) >= 8 else "".join(digits)
    name = re.sub(r"[\d,;\-]+", "", s).strip()
    if not name or not phone:
        return None
    return (name, phone)


# ─── Numbers / rates / dates ───────────────────────────────────────────

def parse_number(message: str) -> int | None:
    digits = re.findall(r"\d+", message)
    if not digits:
        return None
    try:
        return int(digits[0])
    except ValueError:
        return None


def parse_rate(message: str) -> Decimal | None:
    digits = re.findall(r"\d+(?:\.\d+)?", message)
    if not digits:
        return None
    try:
        return Decimal(digits[0])
    except InvalidOperation:
        return None


# ─── Affirmative / negative ────────────────────────────────────────────

_AFFIRMATIVE = {
    "si", "sí", "s", "yes", "ok", "okay", "listo", "dale", "va", "bueno",
    "claro", "perfecto", "esta bien", "está bien", "vale",
}
_NEGATIVE = {"no", "nope", "nel", "nunca", "negativo", "n"}


def is_affirmative(message: str) -> bool:
    return _normalize(message) in _AFFIRMATIVE


def is_negative(message: str) -> bool:
    return _normalize(message) in _NEGATIVE


# ─── Intent keywords ───────────────────────────────────────────────────

def is_trabajar_keyword(message: str) -> bool:
    norm = _normalize(message)
    return norm in {"trabajar", "trabajo", "empleo", "registro", "registrar"}


def is_company_intro_keyword(message: str) -> bool:
    norm = _normalize(message)
    return norm in {"hola", "registro", "empresa", "registrar empresa"}


def is_pausar_keyword(message: str) -> bool:
    return _normalize(message) in {"pausa", "pausar", "stop", "vacaciones", "ocupado"}


def is_reanudar_keyword(message: str) -> bool:
    return _normalize(message) in {"reanudar", "continuar", "listo", "disponible", "activo"}


def is_help_keyword(message: str) -> bool:
    return _normalize(message) in {"ayuda", "help", "menu", "comandos"}


def is_human_keyword(message: str) -> bool:
    return _normalize(message) in {"humano", "human", "persona", "agente"}


def is_job_post_keyword(message: str) -> bool:
    norm = _normalize(message)
    return norm in {"trabajo", "publicar", "nuevo trabajo", "publicar trabajo"}


def is_status_keyword(message: str) -> bool:
    return _normalize(message) in {"estado", "trabajos", "status", "mis trabajos"}


def is_matches_keyword(message: str) -> bool:
    return _normalize(message) in {"matches", "match", "ver matches"}


def is_accept_keyword(message: str) -> bool:
    norm = _normalize(message)
    return norm.startswith("aceptar") or norm == "acepto" or norm == "si"


def is_other_keyword(message: str) -> bool:
    norm = _normalize(message)
    return norm.startswith("otro") or norm == "rechazar"
