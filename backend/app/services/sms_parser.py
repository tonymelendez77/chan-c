import re
import unicodedata


_YES_WORDS = {"si", "sí", "s", "1", "yes"}
_NO_WORDS = {"no", "n", "0"}
_CONTRA_WORDS = {"contra", "contrapropuesta"}
_TRABAJAR_WORDS = {
    "trabajar", "trabajo", "empleo", "oficio",
    "quiero trabajar", "registrar", "registro",
}
_PAUSE_WORDS = {
    "pausa", "pausar", "stop", "para",
    "no mas", "no más", "descanso",
    "vacaciones", "ocupado", "no ofertas",
}
_RESUME_WORDS = {
    "continuar", "reanudar", "listo",
    "disponible", "activo", "resume",
    "ya puedo", "de vuelta",
}


def parse_worker_reply(message_body: str) -> str:
    """Parse an incoming SMS body into SI, NO, CONTRA, TRABAJAR, PAUSAR, REANUDAR, or UNKNOWN.

    Handles accent variations, mixed case, surrounding whitespace,
    and common shorthand.
    """
    # Strip whitespace and non-letter/digit characters from edges
    cleaned = message_body.strip()
    cleaned = re.sub(r"^[^\w]+|[^\w]+$", "", cleaned, flags=re.UNICODE)
    # Normalize unicode (accents) and lowercase
    normalized = unicodedata.normalize("NFC", cleaned).lower()

    if normalized in _YES_WORDS:
        return "SI"
    if normalized in _NO_WORDS:
        return "NO"
    if normalized in _CONTRA_WORDS:
        return "CONTRA"
    if normalized in _TRABAJAR_WORDS:
        return "TRABAJAR"
    if normalized in _PAUSE_WORDS:
        return "PAUSAR"
    if normalized in _RESUME_WORDS:
        return "REANUDAR"
    return "UNKNOWN"
