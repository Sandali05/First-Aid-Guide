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
