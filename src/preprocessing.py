"""Input preprocessing for prescription and patient context before API/LLM calls."""
import re

from config import MAX_PATIENT_CONTEXT_LENGTH, MAX_PRESCRIPTION_LENGTH


def normalize_text(text: str | None, max_length: int) -> str:
    """Clean and truncate text: strip, collapse whitespace, enforce length."""
    if text is None:
        return ""
    s = str(text).strip()
    s = re.sub(r"\s+", " ", s)
    if len(s) > max_length:
        s = s[: max_length - 3].rstrip() + "..."
    return s


def preprocess_prescription(raw: str | None) -> str:
    """Normalize prescription input for retrieval and LLM."""
    return normalize_text(raw, MAX_PRESCRIPTION_LENGTH)


def preprocess_patient_context(raw: str | None) -> str:
    """Normalize patient context for retrieval and LLM."""
    return normalize_text(raw, MAX_PATIENT_CONTEXT_LENGTH)
