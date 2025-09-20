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
