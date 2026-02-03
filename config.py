"""PrescribeMe configuration. API keys are read from env only; never log or expose them."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(PROJECT_ROOT / "chroma_db"))

# Chroma: local (PersistentClient) or cloud (CloudClient)
# For Chroma Cloud: set CHROMA_API_KEY, CHROMA_TENANT, CHROMA_DATABASE
# For HTTP server: set CHROMA_HOST (and optionally CHROMA_API_KEY)
CHROMA_API_KEY = os.getenv("CHROMA_API_KEY", "")
CHROMA_TENANT = os.getenv("CHROMA_TENANT", "")  # Chroma Cloud tenant UUID
CHROMA_DATABASE = os.getenv("CHROMA_DATABASE", "default")  # Chroma Cloud database name
CHROMA_HOST = os.getenv("CHROMA_HOST", "")  # If set (and no tenant), use HttpClient

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")  # Override via env for experimentation
LLM_TIMEOUT_SEC = int(os.getenv("LLM_TIMEOUT_SEC", "60"))
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "2048"))

# Input limits (chars) to avoid oversized API payloads and abuse
MAX_PRESCRIPTION_LENGTH = int(os.getenv("MAX_PRESCRIPTION_LENGTH", "2000"))
MAX_PATIENT_CONTEXT_LENGTH = int(os.getenv("MAX_PATIENT_CONTEXT_LENGTH", "1000"))

# RAG
CHROMA_COLLECTION_NAME = "prescribeme_interactions"
TOP_K_RETRIEVAL = 8
MIN_RELEVANCE_SCORE = 0.3

# Risk levels for UI
RISK_LEVELS = ("low", "moderate", "high", "contraindicated")
