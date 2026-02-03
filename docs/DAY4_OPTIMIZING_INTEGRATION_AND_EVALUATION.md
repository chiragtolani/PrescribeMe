# Day 4 — Optimizing Integration & Application Evaluation

## Checklist

- [x] **Evaluation approach defined (metrics + test set)**  
  - Test set: unit tests in `tests/` (preprocessing, RAG, LLM response parsing, API validation). No gold-label dataset yet; tests use mocks and edge cases (empty input, no evidence, LLM errors).  
  - Metrics: documented in `docs/EVALUATION_AND_PROMPTS.md` (response time, cache hit rate, optional BLEU/reference comparison when gold data exists).

- [x] **Error handling + retries added (API) OR validation rules added (no-code)**  
  - LLM: retries with backoff for `RateLimitError`, `APITimeoutError`, 5xx; configurable `LLM_MAX_RETRIES`, `LLM_TIMEOUT_SEC`.  
  - API: Pydantic validation (prescription required, max lengths); empty prescription → 400; RAG errors → 500 with message.  
  - Frontend: request timeout (90s), user-facing messages for timeout, 429, 5xx; Dismiss on error banner.

- [x] **Prompt/model iteration based on failures**  
  - Prompts centralized in `src/prompts.py` (system prompt, user template, fallbacks). Citation format `[Source N]` and structured output guidance added.  
  - Model override via `LLM_MODEL` in `.env`. Post-processing trims/truncates LLM output and handles empty responses.

- [x] **Latency/cost notes captured**  
  - Timeouts: `LLM_TIMEOUT_SEC` (default 60s), `NEXT_PUBLIC_ANALYZE_TIMEOUT_MS` (default 90s).  
  - Rate limits: retry with backoff on 429; optional in-memory cache for `/api/analyze` (`ENABLE_ANALYZE_CACHE`, `ANALYZE_CACHE_MAX_ENTRIES`) to reduce duplicate LLM calls and cost.  
  - Documented in `docs/EVALUATION_AND_PROMPTS.md` and `.env.example`.

- [x] **Safety/guardrails considered (content, PII, injection)**  
  - API keys: env-only, never logged; `.env.example` and config docstring warn against committing or logging keys.  
  - Input: length limits on prescription and patient context (`MAX_PRESCRIPTION_LENGTH`, `MAX_PATIENT_CONTEXT_LENGTH`); preprocessing normalizes and truncates.  
  - PII: not yet scrubbed from inputs; prompt injection not explicitly mitigated beyond grounding in retrieved evidence (RAG). Documented for future work in evaluation doc.

---

## Artifacts / notes

| Item | Details |
|------|--------|
| **Evaluation dataset link / location** | No dedicated gold-label dataset yet. Tests use `tests/` (mocks + edge cases). Sample data: `data/sample_interactions.json`. For fine-tuning or metrics, see `docs/EVALUATION_AND_PROMPTS.md`. |
| **Metrics used (accuracy, faithfulness, etc.)** | Response time (timeouts + cache), test coverage (preprocessing, RAG, LLM, API). Optional: BLEU or reference-based comparison when gold assessments exist; faithfulness to retrieved sources (manual or automated) noted in evaluation doc. |
| **Top failure modes found** | Empty/missing LLM response; rate limit (429) and timeout; oversized or empty user input; duplicate requests increasing cost/latency. |
| **Fixes applied** | Post-process LLM output (trim, truncate, fallback); retries with backoff for 429/timeout/5xx; input preprocessing and max-length validation; optional analyze cache; frontend timeout and clearer error messages; centralized prompts for iteration. |

---

## Decisions made today (why)

- **Centralized prompts in `src/prompts.py`** — So prompt and model iteration can happen in one place without touching LLM call logic.
- **Custom retry logic for LLM (no SDK max_retries)** — To control backoff (including rate-limit retry-after) and avoid double-retries with SDK.
- **In-memory analyze cache (default on)** — To avoid duplicate LLM calls for identical prescription + patient context and stay under rate limits; can disable with `ENABLE_ANALYZE_CACHE=0`.
- **Input length limits in config** — To bound payload size and reduce abuse; preprocessing enforces them before retrieval/LLM.
- **Pytest suite for preprocessing, RAG, LLM, API** — To lock in behavior and support refactors; LLM/Chroma mocked so CI can run without live APIs.

---

## Blockers / help needed

- None at this time. Possible follow-ups: formal evaluation dataset + metrics (e.g. faithfulness, BLEU), PII scrubbing for patient context, or explicit prompt-injection guardrails if needed for deployment.
