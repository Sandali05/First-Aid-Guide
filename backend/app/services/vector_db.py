# services/vector_db.py
# Minimal Astra DB Vector integration via REST Data API
import requests
import json
import logging
from typing import List, Dict, Any
from . import rules_guardrails as guardrails
from ..config import (
    ASTRA_DB_API_ENDPOINT, ASTRA_DB_KEYSPACE, ASTRA_DB_DATABASE,
    ASTRA_DB_COLLECTION, ASTRA_DB_APPLICATION_TOKEN, has_astra
)

BASE = f"{ASTRA_DB_API_ENDPOINT}/api/json/v1/{ASTRA_DB_KEYSPACE}" if ASTRA_DB_API_ENDPOINT and ASTRA_DB_KEYSPACE else ""
HEADERS = {
    "Content-Type": "application/json",
    "x-cassandra-token": ASTRA_DB_APPLICATION_TOKEN
} if ASTRA_DB_APPLICATION_TOKEN else {"Content-Type": "application/json"}
