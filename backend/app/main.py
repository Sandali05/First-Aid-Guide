# main.py
# FastAPI app exposing chat endpoint for the client.
from fastapi import Depends, FastAPI, HTTPException, status
import requests
from .config import (
    MODEL_PREFERENCE, has_openai, has_groq, has_astra,
    ASTRA_DB_API_ENDPOINT, ASTRA_DB_KEYSPACE, ASTRA_DB_COLLECTION
)
from pydantic import BaseModel
from .agents import conversational_agent, recovery_agent, security_agent, emergency_classifier
from .utils import is_first_aid_related
from typing import Annotated, List, Optional, Literal
from textwrap import dedent
import re


Role = Literal['user', 'assistant', 'system']


class ChatMessage(BaseModel):
    role: Role
    content: str


class ChatContinueRequest(BaseModel):
    messages: List[ChatMessage]
    session_id: Optional[str] = None


FIRST_AID_ONLY_MESSAGE = "This assistant can only respond to first-aid emergencies and treatments."


def _latest_user_message(messages: List[ChatMessage]) -> Optional[ChatMessage]:
    for message in reversed(messages):
        if message.role == "user":
            return message
    return None


def validate_first_aid_intent(payload: ChatContinueRequest) -> ChatContinueRequest:
    latest_user = _latest_user_message(payload.messages)
    if latest_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=FIRST_AID_ONLY_MESSAGE,
        )

    screen = security_agent.safety_screen(latest_user.content)
    if not screen.get("allowed", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=screen.get("reason") or FIRST_AID_ONLY_MESSAGE,
        )

    classification = emergency_classifier.classify_text(screen.get("sanitized", latest_user.content))
    if not classification.get("is_first_aid"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=FIRST_AID_ONLY_MESSAGE,
        )

    return payload


def _normalize_steps(steps) -> str:
    if isinstance(steps, list):
        return "\n".join(f"{idx+1}. {s}" for idx, s in enumerate(steps))
    return str(steps or "")


BODY_PART_KEYWORDS = {
    "head", "face", "scalp", "eye", "ear", "nose", "mouth", "jaw",
    "neck", "throat", "shoulder", "arm", "elbow", "wrist", "hand",
    "finger", "chest", "rib", "abdomen", "stomach", "back", "hip",
    "leg", "knee", "ankle", "foot", "toe", "skin"
}

TREND_PATTERNS = {
    "worse": [
        r"\bgetting worse\b",
        r"\bworsening\b",
        r"\bworse\b",
        r"\bheavier\b",
        r"\bincreasing\b",
        r"\bspreading\b",
        r"\bmore (?:pain|bleeding|swelling|numbness)\b",
    ],
    "better": [
        r"\bgetting better\b",
        r"\bbetter\b",
        r"\bimproving\b",
        r"\bimproved\b",
        r"\bless (?:pain|bleeding|swelling)\b",
        r"\blighter\b",
        r"\bsubsiding\b",
    ],
    "same": [
        r"\babout the same\b",
        r"\bstaying the same\b",
        r"\bno change\b",
        r"\bunchanged\b",
        r"\bstable\b",
    ],
}


def _tailor_steps_for_context(
    original_steps: str,
    triage: dict,
    trend: Optional[str],
    severity_raw: str,
    ambulance_number: str,
    repeated_steps: bool,
) -> str:
    """Provide situation-aware guidance when the base instructions repeat."""

    if not repeated_steps:
        return original_steps

    category = (triage.get("category") or triage.get("emergency") or "").lower()
    severity_normalized = str(severity_raw or "").lower()

    def _format(lines: List[str]) -> str:
        return "\n\n".join(line.strip() for line in lines if line.strip())

    emergency_prompt = (
        f"Call {ambulance_number} or head to the nearest emergency department right away."
        if ambulance_number
        else "Contact emergency services immediately."
    )