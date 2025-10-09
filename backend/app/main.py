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

    if trend == "worse" or severity_normalized in {"high", "severe"}:
        if any(key in category for key in ("fracture", "break")):
            return _format([
                "1. Keep the injured limb immobilized exactly as it is — don’t try to straighten, test, or massage it.",
                f"2. Because the symptoms are getting worse, {emergency_prompt}",
                "3. Continue using cold packs wrapped in cloth for up to 20 minutes at a time and keep the limb elevated above heart level.",
                "4. Watch closely for numbness, tingling, pale or bluish skin, or loss of feeling and report those changes to professionals immediately.",
            ])
        if any(key in category for key in ("bleed", "wound", "lacer", "hemorrhage")):
            return _format([
                "1. Maintain firm, direct pressure on the wound without lifting the cloth or gauze to check it.",
                f"2. Have someone else {emergency_prompt.lower()} while you keep pressure on the area.",
                "3. Keep the injured area elevated above heart level if possible and add clean cloths on top if blood soaks through.",
                "4. If the person gets lightheaded, clammy, or very pale, lie them flat and raise their legs until help arrives.",
            ])
        if any(key in category for key in ("burn", "scald")):
            return _format([
                "1. Continue cooling the burn under cool (not icy) running water for 10–20 minutes total if you haven’t already.",
                "2. Cover it loosely with sterile, non-fluffy dressing or clean cloth after cooling — don’t apply ointments or pop blisters.",
                f"3. Because pain or damage is increasing, {emergency_prompt}",
                "4. Keep jewelry or tight clothing off the area and monitor for difficulty breathing or signs of shock.",
            ])
        if any(key in category for key in ("allergic", "anaphyl")):
            return _format([
                "1. Use an epinephrine auto-injector immediately if one is available and you’re trained.",
                f"2. Because symptoms are escalating, {emergency_prompt}",
                "3. Lay the person flat with legs raised unless they’re struggling to breathe, and loosen tight clothing.",
                "4. If breathing or pulse stops, begin CPR if you’re trained while waiting for emergency responders.",
            ])
        return _format([
            "1. Keep following the earlier first-aid steps exactly as discussed.",
            f"2. Since things are getting worse, {emergency_prompt}",
            "3. Limit movement, keep monitoring vital signs, and prepare for emergency responders with location details.",
            "4. If anyone nearby can assist, have them gather medications, allergies, and medical history for paramedics.",
        ])

    if trend == "same":
        return _format([
            "1. Continue carrying out the first-aid steps we already reviewed.",
            "2. Re-check the area every 10–15 minutes for changes in color, swelling, numbness, or pain spikes.",
            "3. Keep resting the area and avoid anything that might aggravate the injury or condition.",
            f"4. If the situation starts to worsen or new symptoms appear, {emergency_prompt}",
        ])

    if trend == "better":
        return _format([
            "1. Great news — keep gently following the earlier steps while symptoms settle down.",
            "2. Gradually space out ice, compression, or medication only if comfort keeps improving.",
            "3. Protect the area from bumps or strain until it’s fully healed.",
            f"4. If pain returns, discoloration develops, or new symptoms show up, {emergency_prompt}",
        ])

    return _format([
        "1. Continue the prior first-aid guidance as closely as possible.",
        "2. Observe the situation for any new warning signs like spreading pain, fever, numbness, or difficulty breathing.",
        "3. Rest, hydrate, and avoid stress on the affected area while you monitor.",
        f"4. Reach a healthcare professional or {ambulance_number or 'emergency services'} promptly if anything changes or you’re unsure.",
    ])

def _detect_location_known(text: str) -> bool:
    if not text:
        return False
    lowered = text.lower()
    return any(re.search(rf"\b{re.escape(part)}\b", lowered) for part in BODY_PART_KEYWORDS)


def _detect_trend(text: str) -> Optional[str]:
    if not text:
        return None
    lowered = text.lower()
    for label, patterns in TREND_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, lowered):
                return label
    return None


def _acknowledge_user_update(user_text: str, recovered: bool) -> str:
    if recovered:
        return "I’m really glad to hear those symptoms have cleared up."
    trend = _detect_trend(user_text)
    if trend == "worse":
        return "Thanks for telling me it’s getting worse — let’s work to slow it down."
    if trend == "better":
        return "I’m glad it seems to be improving a bit."
    if trend == "same":
        return "Thanks for the update that things feel about the same."
    return ""


def _craft_follow_up_question(
    result: dict,
    history: List[ChatMessage],
    user_text: str,
    recovered: bool,
) -> str:
    triage = result.get("triage", {}) if isinstance(result, dict) else {}
    category = (triage.get("category") or triage.get("emergency") or "concern").lower()
    severity = str(triage.get("severity") or triage.get("level") or "").lower()

    user_history_text = " \n".join(
        msg.content for msg in history if getattr(msg, "role", None) == "user"
    )
    combined_context = f"{user_history_text}\n{user_text}".strip()

    if recovered:
        return ""

    location_known = _detect_location_known(combined_context)
    trend_known = _detect_trend(combined_context)

    severe_categories = {"bleeding", "hemorrhage", "wound"}
    burn_categories = {"burn", "scald"}
    sprain_categories = {"sprain", "strain", "bruise", "contusion"}
    fracture_categories = {"fracture", "break"}

    if severity in {"high", "severe"}:
        return (
            "Do you notice any life-threatening signs such as heavy bleeding that won’t slow down, trouble breathing, or loss of consciousness?"
        )

    if category in severe_categories or any(cat in category for cat in severe_categories):
        if not location_known:
            return "Where is the bleeding coming from and how wide is the injured area?"
        if not trend_known:
            return "Is the bleeding slowing down, staying the same, or getting heavier despite pressure?"
        return "Have you been able to keep steady pressure with clean fabric or gauze on it for a full 10 minutes yet?"

    if category in burn_categories:
        if not location_known:
            return "Which part of the body was burned and how large is the area?"
        return "Are there blisters, charring, or deep white patches on the burn?"

    if category in sprain_categories:
        if not trend_known:
            return "Is the swelling improving, staying the same, or getting worse right now?"
        return "Can you still move the area, or does the pain spike when you try to bear weight or grip?"

    if category in fracture_categories:
        return "Can you avoid moving the injured limb and are you seeing any obvious deformity or numbness?"

    if not trend_known:
        return "Are the symptoms improving, staying the same, or getting worse at this moment?"

    if not location_known:
        return "Where on your body are you feeling this the most?"

    return "Is there anything new or changing that I should know about right now?"
