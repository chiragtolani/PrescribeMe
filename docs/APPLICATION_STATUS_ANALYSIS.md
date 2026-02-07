# PrescribeMe — Application Status: Completed vs Pending

Summary of what is **completed** and what is **pending** as of this analysis.

---

## Completed

### Core product

| Area | Status | Notes |
|------|--------|------|
| **RAG pipeline** | Done | Retrieval (Chroma + OpenAI embeddings), LLM synthesis (OpenAI), preprocessing, centralized prompts. |
| **Prescription analysis** | Done | User enters prescription + optional patient context → backend runs retrieval + LLM → returns assessment + retrieved evidence. |
| **Evidence grounding** | Done | LLM answers only from retrieved chunks; citations `[Source N]`; uncertainty when evidence is weak. |
| **Patient context** | Done | Age, weight, conditions, current meds sent to API and used in query + LLM prompt. |

### Backend (API)

| Area | Status | Notes |
|------|--------|------|
| **Endpoints** | Done | `POST /api/analyze`, `POST /api/init-kb`, `GET /api/health`. |
| **Validation** | Done | Pydantic: prescription required, max lengths; empty prescription → 400. |
| **CORS** | Done | Configurable `CORS_ORIGINS`; defaults include localhost. |
| **LLM integration** | Done | Timeouts, retries (rate limit/timeout/5xx), `max_tokens`, response parsing and fallbacks. |
| **Optional cache** | Done | In-memory cache for identical analyze requests; configurable, max entries limit. |
| **Input preprocessing** | Done | Normalize + length limits for prescription and patient context before retrieval/LLM. |

### Frontend

| Area | Status | Notes |
|------|--------|------|
| **Stack** | Done | Next.js 14 (App Router), Tailwind, Framer Motion, Lucide. |
| **Screens** | Done | Single main view: sidebar (PatientContext, InitKB) + main (PrescriptionForm, Results). |
| **API client** | Done | Centralized `lib/api.ts` with timeout (AbortController), error parsing, user-facing messages. |
| **Loading / errors** | Done | Loading state on submit; error banner with message + Dismiss. |
| **Evidence display** | Done | Assessment text + expandable EvidenceCard list with RiskBadge. |
| **Init KB** | Done | Button to run init-kb; success/error feedback. |

### Knowledge base and data

| Area | Status | Notes |
|------|--------|------|
| **KB loader** | Done | Loads `sample_interactions.json`, `drugbank_interactions.json`, `pubmed_abstracts.json` (if present). |
| **Chroma** | Done | Local (PersistentClient) or Chroma Cloud (CloudClient) or HTTP (HttpClient). |
| **Sample data** | Done | `data/sample_interactions.json` in repo. |
| **PubMed data** | Done | `data/pubmed_abstracts.json` in repo; script `scripts.fetch_pubmed` available. |
| **Build path** | Done | UI “Initialize knowledge base” or `python -m scripts.build_kb`; batches of 100, replaces collection. |

### Testing

| Area | Status | Notes |
|------|--------|------|
| **Unit tests** | Done | `tests/test_preprocessing.py`, `test_rag.py`, `test_llm.py`, `test_api.py` (pytest). |
| **Coverage** | Done | Preprocessing, RAG flow (mocked), LLM response handling, API validation, cache. |
| **CI-ready** | Done | No live OpenAI/Chroma required for tests. |

### Deployment and docs

| Area | Status | Notes |
|------|--------|------|
| **Deploy guide** | Done | `DEPLOYMENT.md`: Vercel (frontend) + Render (API). |
| **Blueprint** | Done | `render.yaml` for Render. |
| **Chroma Cloud** | Done | `docs/CHROMA_CLOUD_SETUP.md`, `docs/KB_AND_CHROMA.md`. |
| **Data guide** | Done | `data/README.md`: sample, DrugBank, PubMed formats and scripts. |
| **Evaluation / prompts** | Done | `docs/EVALUATION_AND_PROMPTS.md` (metrics, tuning, fine-tuning notes). |
| **Progress tracking** | Done | Day 4 and Day 5 docs in `docs/`. |

### Security and robustness

| Area | Status | Notes |
|------|--------|------|
| **API keys** | Done | Env-only; no keys in code or logs; `.env.example` and config warnings. |
| **Input limits** | Done | Max lengths for prescription and patient context; preprocessing enforces. |
| **Error handling** | Done | Backend returns 400/500 with message; frontend shows clear errors and timeout. |

### Optional / extras

| Area | Status | Notes |
|------|--------|------|
| **Streamlit UI** | Done | `app.py` for alternative UI. |
| **DrugBank script** | Done | `scripts.ingest_drugbank` to produce `drugbank_interactions.json` from CSV. |

---

## Pending / not done

### Data and KB

| Item | Priority | Notes |
|------|----------|--------|
| **DrugBank JSON in repo** | Optional | `data/drugbank_interactions.json` is not in repo; user must run `ingest_drugbank` with their DrugBank CSV. Doc and script are ready. |

### API and backend

| Item | Priority | Notes |
|------|----------|--------|
| **API authentication** | Medium | No auth on `/api/analyze` or `/api/init-kb`. Fine for demo; for production you may want API keys or OAuth. |
| **Rate limiting** | Medium | No per-IP or per-user rate limit on endpoints. OpenAI retries handle provider limits; app-level limits would protect your API. |
| **Request/response logging** | Low | No middleware logging requests/responses. Could add with PII scrubbing for debugging/monitoring. |

### Security and compliance

| Item | Priority | Notes |
|------|----------|--------|
| **PII scrubbing** | Medium | Patient context is not scrubbed before sending to OpenAI. For sensitive deployments, add redaction or local-only context. |
| **Prompt-injection guardrails** | Low | RAG grounding reduces risk; no explicit checks for adversarial or off-topic input. |

### Evaluation and quality

| Item | Priority | Notes |
|------|----------|--------|
| **Gold-label evaluation set** | Low | No curated (prescription → expected assessment) dataset; only unit tests and mocks. |
| **Structured metrics** | Low | No BLEU/faithfulness/latency tracking in code; ideas documented in `EVALUATION_AND_PROMPTS.md`. |
| **Fine-tuning pipeline** | Low | Dataset format and ideas documented; no script or pipeline to produce training data. |

### Frontend and UX

| Item | Priority | Notes |
|------|----------|--------|
| **Clear form** | Low | No “Clear” for prescription text. |
| **Copy assessment** | Low | No “Copy assessment” for clinicians. |
| **Progress indicator** | Low | Only generic “Analyzing…”; no retrieval vs LLM phase. |
| **Mobile layout** | Medium | Sidebar may need collapsible or stacked layout on small screens. |
| **Accessibility** | Medium | ARIA, keyboard navigation, and screen-reader support not verified. |
| **Patient context validation** | Low | No client-side checks (e.g. age range, weight units). |

### Testing and operations

| Item | Priority | Notes |
|------|----------|--------|
| **E2E tests** | Low | No Playwright/Cypress (or similar) E2E; only backend/unit tests. |
| **Screenshots / demo assets** | Low | No linked screenshots or demo walkthrough in repo. |
| **User testing** | Low | No formal clinician or user testing reported. |

---

## Quick reference

- **Ready for:** Local use, demos, Vercel + Render deployment with sample + PubMed (and optional DrugBank after ingest).
- **Before production at scale:** Consider API auth, rate limiting, PII handling, and mobile/accessibility.
- **Before formal evaluation:** Add gold-label test set and metrics (see `docs/EVALUATION_AND_PROMPTS.md`).
