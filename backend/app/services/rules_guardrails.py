"""Utilities for enforcing YAML-defined guardrails policies."""
from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Dict

import yaml

LOGGER = logging.getLogger(__name__)
GUARDRAILS_PATH = Path(__file__).resolve().parent.parent / "guardrails.yaml"

