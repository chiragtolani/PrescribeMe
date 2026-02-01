"""PrescribeMe configuration."""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(PROJECT_ROOT / "chroma_db"))

# OpenAI
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-4o-mini"  # Compact model for cost-effective reasoning

# RAG
CHROMA_COLLECTION_NAME = "prescribeme_interactions"
TOP_K_RETRIEVAL = 8
MIN_RELEVANCE_SCORE = 0.3

# Risk levels for UI
RISK_LEVELS = ("low", "moderate", "high", "contraindicated")
