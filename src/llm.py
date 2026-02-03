"""LLM synthesis for risk assessment, explanations, and alternatives (evidence-grounded)."""
import time

from openai import OpenAI
from openai import APITimeoutError, RateLimitError, APIStatusError

from config import (
    LLM_MAX_RETRIES,
    LLM_MAX_TOKENS,
    LLM_MODEL,
    LLM_TIMEOUT_SEC,
    OPENAI_API_KEY,
)
from src.prompts import (
    FALLBACK_NO_EVIDENCE,
    FALLBACK_NO_RESPONSE,
    SYSTEM_PROMPT,
    USER_MESSAGE_TEMPLATE,
)


def get_llm_client(timeout: float | None = None) -> OpenAI:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set.")
    return OpenAI(
        api_key=OPENAI_API_KEY,
        timeout=(timeout or LLM_TIMEOUT_SEC),
        max_retries=0,  # We implement retries with backoff ourselves
    )


def _postprocess_response(content: str | None) -> str:
    """Clean and truncate LLM output for display."""
    if content is None or not isinstance(content, str):
        return FALLBACK_NO_RESPONSE
    text = content.strip()
    if not text:
        return FALLBACK_NO_RESPONSE
    # Optional: truncate if extremely long (e.g. model ignored max_tokens)
    max_display = 8000
    suffix = "\n\n[Response truncated.]"
    if len(text) > max_display:
        text = text[: max_display - len(suffix)].rstrip() + suffix
    return text


def _build_user_message(prescription_text: str, patient_context: str, retrieved_chunks: list[dict]) -> str:
    evidence_block = "\n\n---\n\n".join(
        [
            f"[Source {i+1}] (relevance: {c.get('score', 0):.2f})\n{c.get('document', '')}"
            for i, c in enumerate(retrieved_chunks)
        ]
    )
    return USER_MESSAGE_TEMPLATE.format(
        prescription_text=prescription_text,
        patient_context=patient_context or "None",
        evidence_block=evidence_block,
    )


def synthesize_assessment(
    prescription_text: str,
    patient_context: str,
    retrieved_chunks: list[dict],
    model: str = LLM_MODEL,
) -> str:
    """Synthesize risk assessment and recommendations from retrieved evidence.
    Handles API latency (timeout), rate limits (retry with backoff), and response parsing.
    """
    if not retrieved_chunks:
        return FALLBACK_NO_EVIDENCE

    user_message = _build_user_message(prescription_text, patient_context or "", retrieved_chunks)
    client = get_llm_client(timeout=float(LLM_TIMEOUT_SEC))

    last_error: Exception | None = None
    for attempt in range(LLM_MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.2,
                max_tokens=LLM_MAX_TOKENS,
            )
            raw = response.choices[0].message.content if response.choices else None
            return _postprocess_response(raw)
        except RateLimitError as e:
            last_error = e
            retry_after = getattr(e, "retry_after", None) or min(2 ** attempt, 60)
            if attempt < LLM_MAX_RETRIES - 1:
                time.sleep(retry_after)
            continue
        except APITimeoutError as e:
            last_error = e
            if attempt < LLM_MAX_RETRIES - 1:
                time.sleep(1.0 * (attempt + 1))
            continue
        except APIStatusError as e:
            last_error = e
            if e.status_code and 500 <= e.status_code < 600 and attempt < LLM_MAX_RETRIES - 1:
                time.sleep(1.0 * (attempt + 1))
                continue
            raise

    if last_error:
        raise last_error
    return FALLBACK_NO_RESPONSE
