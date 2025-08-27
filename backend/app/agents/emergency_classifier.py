"""Emergency classifier heuristics and allow-list gate."""
from __future__ import annotations

import re
from typing import Dict, List, Tuple

from ..utils import FIRST_AID_KEYWORDS, basic_sanitize

# Minimal rule-based mapping used after the allow-list gate passes.
_CATEGORY_RULES: List[Tuple[str, List[str]]] = [
    ("bleeding", ["bleed", "blood", "cut", "lacer", "wound", "hemorrh"]),
    ("burn", ["burn", "scald", "blister", "char"]),
    ("choking", ["chok", "airway", "heimlich", "cant breathe", "can't breathe"]),
    ("allergic reaction", ["allerg", "anaphyl", "hives", "swelling"]),
    ("bruise", ["bruise", "contusion"]),
    ("sprain", ["sprain", "strain", "twist"]),
    ("fracture", ["fracture", "broken bone", "break", "crack"]),
    ("fainting", ["faint", "passed out", "dizzy", "lightheaded"]),
    ("headache", ["headache", "migraine"]),
    ("poisoning", ["poison", "overdose", "toxic"]),
]

_SEVERITY_HINTS = {
    "bleeding": "medium",
    "burn": "medium",
    "choking": "high",
    "allergic reaction": "high",
    "fracture": "high",
}