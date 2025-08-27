# agents/conversational_agent.py
# Orchestrates the flow among classifier, instruction, verification, and scoring.
from typing import Dict, List, Optional
from difflib import get_close_matches
import re
from . import (
    emergency_classifier,
    instruction_agent,
    verification_agent,
    security_agent,
    recovery_agent,
)
from ..services import mcp_server
import logging
from ..services.risk_confidence import score_risk_confidence
from ..utils import is_first_aid_related


KNOWN_EMERGENCY_TERMS = {
    "bleeding", "bruise", "burn", "scald", "sprain", "strain",
    "fracture", "break", "choke", "allergic", "anaphylaxis", "faint",
    "dizzy", "headache", "migraine", "cut", "laceration", "wound",
    "pain",
}


def _gather_user_context(history: Optional[List[Dict]], user_input: str) -> str:
    """Return a condensed text string describing the recent user context."""
    if not history:
        return user_input
    user_turns = [m.get("content", "")
                  for m in history if m.get("role") == "user"]
    user_turns.append(user_input)
    # Keep the last 3 user turns to stay focused on the current issue.
    return " \n".join(user_turns[-3:]).strip()
