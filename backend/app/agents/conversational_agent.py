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


def _detect_clarification_prompt(text: str) -> Optional[str]:
    """Look for likely typos or ambiguous medical terms and craft a prompt."""
    tokens = re.findall(r"[a-zA-Z']+", text.lower())
    for token in tokens:
        if token in KNOWN_EMERGENCY_TERMS or len(token) < 4:
            continue
        match = get_close_matches(
            token, KNOWN_EMERGENCY_TERMS, n=1, cutoff=0.78)
        if match:
            guess = match[0]
            return (
                f"Got it — when you say “{token},” do you mean “{guess}” (an injury to the skin causing discoloration) "
                "or something else? If it’s that injury I can walk you through first-aid. If it’s different, could you clarify?"
            )
    return None


def handle_message(
    user_input: str,
    history: Optional[List[Dict]] = None,
    session_id: Optional[str] = None,
) -> Dict:
    try:
        # 0) Pull recent conversational context so the pipeline sees the full story.
        context_text = _gather_user_context(history, user_input)

        # 1) Security & privacy layer
        sec = security_agent.protect(context_text)

        latest_security = security_agent.protect(user_input)
        sanitized_latest = latest_security.get("sanitized", user_input)
        security_scope_hint = latest_security.get("in_scope")

        classifier_gate = emergency_classifier.classify_text(sanitized_latest)

        # 2) Detect recovery cues so downstream components can conclude safely.
        recovery = recovery_agent.detect(history or [], user_input)

        in_scope = classifier_gate.get("is_first_aid", False)
        if security_scope_hint is False:
            in_scope = False
        elif security_scope_hint is True:
            in_scope = True

        conversation_meta = {
            "context": context_text,
            "recovered": recovery.get("recovered"),
            "in_scope": in_scope,
            "needs_clarification": False,
            "clarification_prompt": None,
            "classifier_gate": classifier_gate,
        }
        if session_id:
            conversation_meta["session_id"] = session_id

        if not in_scope:
            risk_stub = score_risk_confidence(
                {"category": "out_of_scope", "severity": "low"},
                {"passed": False, "skipped": True},
            )
            return {
                "rejected": True,
                "reason": "This assistant can only discuss first-aid emergencies and treatments.",
                "security": {**sec, "latest_sanitized": sanitized_latest},
                "triage": {
                    "category": "out_of_scope",
                    "severity": "low",
                    "keywords": [],
                    "confidence": classifier_gate.get("confidence", 0.0),
                },
                "instructions": {"steps": []},
                "verification": {"passed": False, "skipped": True},
                "risk_confidence": risk_stub,
                "conversation": conversation_meta,
                "recovery": recovery,
            }
