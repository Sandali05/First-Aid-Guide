"""Input sanitisation and scope enforcement utilities."""
from __future__ import annotations

import re
from typing import Dict

from ..services import rules_guardrails
from ..utils import basic_sanitize, is_first_aid_related
