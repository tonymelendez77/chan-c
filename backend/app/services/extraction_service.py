import json
import logging

import anthropic

from app.core.config import settings

logger = logging.getLogger(__name__)

EXTRACTION_MODEL = "claude-sonnet-4-20250514"

SYSTEM_PROMPT = (
    "You are a data extraction assistant for CHAN-C, "
    "a labor marketplace in Guatemala. Extract structured "
    "information from a phone call transcript between "
    "a CHAN-C agent and an informal construction worker. "
    "The conversation is in Spanish. "
    "Return ONLY valid JSON. No explanation, no markdown."
)

CONFIRMATION_SCHEMA = """\
Extract the following from the transcript and return as JSON:
{
  "can_cover": ["list of things worker confirmed they can do"],
  "cannot_cover": ["list of things they said they cannot do"],
  "availability_notes": "any notes about their schedule",
  "final_status": "interested" | "not_interested" | "interested_with_conditions",
  "confidence_score": 0.0 to 1.0
}
"""

COUNTEROFFER_SCHEMA = """\
Extract the following from the transcript and return as JSON:
{
  "proposed_rate": numeric or null,
  "proposed_dates": "text description of proposed dates",
  "counteroffer_notes": "any conditions or special requirements",
  "final_status": "interested_with_conditions",
  "confidence_score": 0.0 to 1.0
}
"""


def _empty_result(call_type: str) -> dict:
    """Return a low-confidence result when transcript is missing or too short."""
    base = {
        "final_status": "interested_with_conditions",
        "confidence_score": 0.0,
        "requires_admin_review": True,
    }
    if call_type == "counteroffer":
        base.update({
            "proposed_rate": None,
            "proposed_dates": "",
            "counteroffer_notes": "Transcript unavailable or too short",
        })
    else:
        base.update({
            "can_cover": [],
            "cannot_cover": [],
            "availability_notes": "Transcript unavailable or too short",
        })
    return base


async def extract_from_transcript(transcript: str, call_type: str) -> dict:
    """Send transcript to Claude API and extract structured data.

    Returns a dict matching the confirmation or counteroffer schema.
    On failure, returns a low-confidence result flagged for admin review.
    """
    if not transcript or len(transcript.strip()) < 30:
        logger.warning("Transcript too short for extraction (len=%d)", len(transcript or ""))
        return _empty_result(call_type)

    schema = COUNTEROFFER_SCHEMA if call_type == "counteroffer" else CONFIRMATION_SCHEMA
    user_message = f"{schema}\n\nTranscript:\n{transcript}"

    try:
        client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = client.messages.create(
            model=EXTRACTION_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        raw_text = response.content[0].text.strip()
        # Strip markdown fences if present
        if raw_text.startswith("```"):
            raw_text = raw_text.split("\n", 1)[1] if "\n" in raw_text else raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3].strip()

        result = json.loads(raw_text)
        result.setdefault("confidence_score", 0.5)
        result["requires_admin_review"] = result.get("confidence_score", 0) < settings.CONFIDENCE_THRESHOLD
        logger.info("Extraction complete: status=%s, confidence=%.2f",
                     result.get("final_status"), result.get("confidence_score", 0))
        return result

    except json.JSONDecodeError as e:
        logger.error("Failed to parse extraction JSON: %s", e)
        result = _empty_result(call_type)
        result["counteroffer_notes" if call_type == "counteroffer" else "availability_notes"] = (
            f"JSON parse error: {raw_text[:200]}"
        )
        return result

    except Exception as e:
        logger.error("Extraction API call failed: %s", e)
        return _empty_result(call_type)
