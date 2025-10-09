# utils.py
from typing import List, Dict, Optional
import re


FIRST_AID_KEYWORDS = {
    "bleed", "bleeding", "blood", "cut", "wound", "injury", "hurt",
    "pain", "ache", "aching", "burn", "scald", "bruise", "fracture",
    "sprain", "strain", "twist", "swelling", "numb", "tingling",
    "broken", "break", "dizzy", "faint", "choke", "choking", "allergic",
    "anaphylaxis", "sting", "bite", "rash", "fever", "headache",
    "migraine", "breathing", "trouble breathing", "emergency",
    "first aid", "ambulance", "wheeze", "seizure", "bleeder", "hemorrhage",
    "poison", "poisoning", "stroke", "heart", "cardiac", "cpr",
}

GENERIC_TRIAGE_CATEGORIES = {
    "", "unknown", "concern", "issue", "situation", "emergency",
    "medical emergency", "non-urgent",
}

# Very small sanitizer aligned with guardrails checks
def basic_sanitize(text: str) -> str:
    # Remove suspicious characters while preserving normal punctuation
    return re.sub(r"[\x00-\x1f\x7f]", " ", text).strip()

def chunk_text(text: str, limit_tokens: int = 500, approx_chars_per_token: int = 3) -> List[str]:
    # Simple chunker to avoid provider 400 errors due to long inputs
    max_len = limit_tokens * approx_chars_per_token
    return [text[i:i+max_len] for i in range(0, len(text), max_len)]


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z]+", text.lower())
