"""Utilities for enforcing YAML-defined guardrails policies."""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict

import yaml

LOGGER = logging.getLogger(__name__)
GUARDRAILS_PATH = Path(__file__).resolve().parent.parent / "guardrails.yaml"


def _load_rules() -> Dict:
    if not GUARDRAILS_PATH.exists():
        LOGGER.warning("Guardrails config missing at %s; falling back to defaults", GUARDRAILS_PATH)
        return {}
    try:
        with GUARDRAILS_PATH.open("r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle) or {}
    except (OSError, yaml.YAMLError) as exc:
        LOGGER.warning("Unable to load guardrails config: %s", exc)
        return {}

    if not isinstance(data, dict):
        LOGGER.warning("Guardrails config must be a mapping; using empty defaults")
        return {}

    return data