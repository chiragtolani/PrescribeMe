# Evaluation, Prompts, and Fine-Tuning

## Prompt engineering

- **Templates:** Edit `src/prompts.py` to change the system prompt and user message template. Tune for clarity, citation format (`[Source N]`), and risk-level wording.
- **Model:** Override via `LLM_MODEL` in `.env` (e.g. `gpt-4o` for higher quality; `gpt-4o-mini` for cost/speed).
- **Output quality:** Use the same prescription + patient context and compare outputs across prompt or model changes. Check for accuracy, relevance, coherence, and correct citation of retrieved sources.

## Performance and evaluation

- **Response time:** LLM timeout is configurable via `LLM_TIMEOUT_SEC` (default 60s). Frontend request timeout is `NEXT_PUBLIC_ANALYZE_TIMEOUT_MS` (default 90s).
- **Rate limits:** The app retries on OpenAI rate-limit (429) with backoff. Optional in-memory cache for `/api/analyze` reduces duplicate LLM calls; set `ENABLE_ANALYZE_CACHE=0` to disable.
- **Quality metrics:** For systematic evaluation, consider logging (prescription, patient_context, assessment, retrieved IDs) and comparing against gold labels (e.g. expert risk level, expected citations). BLEU or similar metrics can be used for text-generation comparison if you have reference summaries.

## Fine-tuning (optional)

If you use a model that supports fine-tuning (e.g. OpenAI fine-tuning):

1. **Dataset format:** Compile (input, output) pairs: input = prescription + patient context + retrieved evidence block; output = desired assessment text (risk level, explanation, alternatives, caveats).
2. **Data sources:** Use `data/sample_interactions.json` and any domain-specific interaction summaries. Preprocess into the same structure as the current user message (see `src/prompts.USER_MESSAGE_TEMPLATE`).
3. **Preprocessing:** Clean and normalize text; ensure no PII in training data. Follow your provider’s fine-tuning format (e.g. JSONL for OpenAI).

The current app does not run fine-tuning; it uses the base (or already fine-tuned) model. Use this section as a guide when you are ready to create and submit a fine-tuning dataset.
