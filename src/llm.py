"""LLM synthesis for risk assessment, explanations, and alternatives (evidence-grounded)."""
from openai import OpenAI

from config import LLM_MODEL, OPENAI_API_KEY


def get_llm_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=OPENAI_API_KEY)


SYSTEM_PROMPT = """You are PrescribeMe, an AI prescription review assistant. You analyze drug combinations using ONLY the retrieved evidence provided. You must:
1. Assess interaction risk (low / moderate / high / contraindicated) based on the evidence.
2. Explain why the interaction matters and when it is clinically relevant, citing the retrieved sources.
3. Suggest safer alternatives only when the evidence supports them.
4. Clearly signal uncertainty: if evidence is weak or insufficient, say so explicitly. Do not guess.
You never invent interactions or citations. If the retrieved context does not support a claim, say "Insufficient evidence" or "Not found in provided sources."
Output in a structured, clear way suitable for display in a clinical decision-support interface."""


def synthesize_assessment(
    prescription_text: str,
    patient_context: str,
    retrieved_chunks: list[dict],
    model: str = LLM_MODEL,
) -> str:
    """Synthesize risk assessment and recommendations from retrieved evidence."""
    if not retrieved_chunks:
        return (
            "No relevant interaction evidence was retrieved for this prescription. "
            "Consider checking drug names and trying again, or consult a drug reference."
        )

    evidence_block = "\n\n---\n\n".join(
        [
            f"[Source {i+1}] (relevance: {c.get('score', 0):.2f})\n{c.get('document', '')}"
            for i, c in enumerate(retrieved_chunks)
        ]
    )

    user_message = f"""Prescription (drugs to review):
{prescription_text}

Patient context (if provided):
{patient_context or "None"}

Retrieved interaction evidence (use only this to ground your response):
{evidence_block}

Provide: (1) Overall risk level, (2) Explanation with citations to the sources above, (3) Safer alternatives if supported by evidence, (4) Any uncertainty or limitations."""

    client = get_llm_client()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content or "No response generated."
