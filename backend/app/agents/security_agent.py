"""Input sanitisation and scope enforcement utilities."""
from __future__ import annotations

import re
from typing import Dict

from ..services import rules_guardrails
from ..utils import basic_sanitize, is_first_aid_related

_OFF_TOPIC_KEYWORDS = {
    "crypto",
    "bitcoin",
    "stock",
    "stocks",
    "invest",
    "investment",
    "homework",
    "assignment",
    "movie",
    "film",
    "recipe",
    "cook",
    "cooking",
    "code",
    "coding",
    "program",
    "programming",
    "travel",
    "vacation",
    "sports",
    "basketball",
    "football",
}


def safety_screen(user_text: str) -> Dict[str, str]:
    """Run guardrail and keyword checks to ensure the text is in scope."""

    sanitized = basic_sanitize(user_text)
    policy_decision = rules_guardrails.policy_check(sanitized)
    if not policy_decision.get("allowed", False):
        return {
            "allowed": False,
            "reason": policy_decision.get("reason")
            or "This assistant can only discuss first-aid topics.",
            "sanitized": sanitized,
        }
