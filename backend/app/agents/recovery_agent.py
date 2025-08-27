"""Agent utilities for detecting recovery cues in user conversations."""
from typing import Iterable, List, Optional, Union, Dict
import re

# Patterns indicating the user reports resolution of their symptoms.
RECOVERY_PATTERNS: List[str] = [
    r"\ball good now\b",
    r"\ball better now\b",
    r"\bfeeling (?:fine|okay|ok|better) now\b",
    r"\bfeels? (?:fine|okay|ok|better) now\b",
    r"\bno(?: longer| more)? (?:hurting|hurt|pain|bleeding)(?: anymore)?\b",
    r"\bnot (?:painful|hurting|bleeding) anymore\b",
    r"\bpain (?:is )?gone\b",
    r"\bbleeding (?:has )?stopped\b",
    r"\b(?:pain|hurting|bleeding) (?:has )?stopped\b",
    r"\bit'?s healed now\b",
    r"\byes(?:,)? it (?:has )?stopped\b",
    r"\byep(?:,)? it (?:has )?stopped\b",
]

CONFIRMATION_ONLY_PATTERNS: List[str] = [
    r"\byes\b",
    r"\byeah\b",
    r"\byep\b",
    r"\bthanks\b",
    r"\bthank you\b",
    r"\bappreciate it\b",
]

MessageLike = Union[Dict[str, str], object]


def _extract_user_content(message: MessageLike) -> Optional[str]:
    """Return the user-authored text from a chat message like object."""
    if isinstance(message, dict):
        if message.get("role") != "user":
            return None
        return message.get("content") or ""
    role = getattr(message, "role", None)
    if role != "user":
        return None
    return getattr(message, "content", "") or ""


def _extract_previous_user_text(
    history: Optional[Iterable[MessageLike]], latest_input: str
) -> Optional[str]:
    """Return the most recent user-authored text preceding the latest input."""
    if not history:
        return None

    prev: Optional[str] = None
    for item in history:
        content = _extract_user_content(item)
        if content is not None:
            prev = content

    if prev == latest_input:
        return None
    return prev
