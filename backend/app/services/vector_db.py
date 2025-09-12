# services/vector_db.py
# Minimal Astra DB Vector integration via REST Data API
import requests, json
import logging
from typing import List, Dict, Any
from . import rules_guardrails as guardrails
from ..config import (
    ASTRA_DB_API_ENDPOINT, ASTRA_DB_KEYSPACE, ASTRA_DB_DATABASE,
    ASTRA_DB_COLLECTION, ASTRA_DB_APPLICATION_TOKEN, has_astra
)
