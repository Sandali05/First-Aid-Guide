# agents/instruction_agent.py
# Generates step-by-step first-aid instructions grounded by retrieved guides.
from typing import List, Dict
import logging
import requests
from ..config import MODEL_PREFERENCE, OPENAI_API_KEY, GROQ_API_KEY, EMBEDDING_MODEL, has_openai
from ..services import vector_db
from ..utils import chunk_text

OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
OPENAI_EMBED_URL = "https://api.openai.com/v1/embeddings"

def embed(text: str) -> List[float]:
    # Use OpenAI embeddings to query Astra vector search
    if not has_openai():
        logging.warning("OPENAI_API_KEY not set; returning empty embedding")
        return []
    try: