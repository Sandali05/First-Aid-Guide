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
