# Whimsical Architecture Diagram Prompt for PrescribeMe

Copy the prompt below into Whimsical to generate a comprehensive application architecture flowchart.

---

## Prompt for Whimsical

Create a detailed, production-ready application architecture flowchart for **PrescribeMe**, a prescription risk and drug interaction intelligence system. The diagram should show all components, data flows, user interactions, and future scalability considerations.

### Architecture Overview

**Application Type:** RAG (Retrieval-Augmented Generation) web application for clinical decision support

**Deployment:**
- Frontend: Next.js 14 (App Router) hosted on Vercel
- Backend API: FastAPI (Python) hosted on Render
- Vector Database: Chroma Cloud (persistent, cloud-hosted)
- LLM Provider: OpenAI (embeddings + synthesis)

### User Flows to Include

1. **Knowledge Base Initialization Flow:**
   - User clicks "Initialize knowledge base" in UI
   - Frontend → POST /api/init-kb → Backend API
   - Backend loads data from: sample_interactions.json, drugbank_interactions.json (optional), pubmed_abstracts.json (optional)
   - Each document is embedded using OpenAI text-embedding-3-small
   - Embeddings + metadata stored in Chroma Cloud collection "prescribeme_interactions"
   - Response returns document count

2. **Prescription Analysis Flow:**
   - User enters prescription text (drug names) and optional patient context (age, weight, conditions, current meds)
   - Frontend → POST /api/analyze with prescription_text + patient_context
   - Backend combines prescription + patient context into query string
   - Query embedded with OpenAI text-embedding-3-small
   - Chroma Cloud queried for top-8 similar documents (by embedding similarity)
   - Retrieved chunks (with metadata: drug_a, drug_b, risk, summary, evidence, alternatives) passed to LLM
   - LLM (gpt-4o-mini, temperature 0.2) synthesizes assessment using system prompt that enforces strict grounding
   - Response includes: assessment text, retrieved chunks with relevance scores
   - Frontend displays assessment and expandable "Retrieved evidence" cards

### Components to Show

**Frontend (Next.js on Vercel):**
- Header component (title, description)
- PatientContext sidebar component (age, weight, conditions, current meds inputs)
- PrescriptionForm component (textarea for prescription, Analyze button)
- Results component (assessment display)
- EvidenceCard components (expandable cards showing drug pair, risk badge, relevance score, summary, evidence, alternatives)
- InitKB component (Initialize knowledge base button)
- API client (lib/api.ts) - fetch calls to backend

**Backend API (FastAPI on Render):**
- POST /api/analyze endpoint (prescription analysis)
- POST /api/init-kb endpoint (knowledge base initialization)
- GET /api/health endpoint (health check)
- CORS middleware (allows Vercel frontend origin)
- Error handling middleware

**RAG Pipeline (Python modules):**
- src/rag.py - run_analysis() orchestrator
- src/retrieval.py - retrieve_for_prescription() (embeds query, queries Chroma)
- src/llm.py - synthesize_assessment() (system prompt + evidence block → LLM)
- src/embeddings.py - embed_texts(), embed_single() (OpenAI API calls)
- src/chroma_store.py - get_chroma_client() (CloudClient for Chroma Cloud), build_knowledge_base() (loads data, embeds, upserts to Chroma)
- src/kb_loader.py - load_sample(), load_drugbank(), load_pubmed(), load_all_documents()

**External Services:**
- Chroma Cloud (vector database) - CloudClient connection with api_key, tenant, database
- OpenAI API - embeddings (text-embedding-3-small) and LLM (gpt-4o-mini)

**Data Sources:**
- data/sample_interactions.json (curated drug-drug interactions)
- data/drugbank_interactions.json (DrugBank export, converted via scripts/ingest_drugbank)
- data/pubmed_abstracts.json (PubMed abstracts fetched via scripts/fetch_pubmed)

**Scripts (one-time data preparation):**
- scripts/fetch_pubmed.py (queries NCBI E-utilities API, writes pubmed_abstracts.json)
- scripts/ingest_drugbank.py (converts DrugBank CSV to drugbank_interactions.json)
- scripts/build_kb.py (runs build_knowledge_base to populate Chroma)

### Data Flow Details

1. **KB Build Flow:**
   - Data files (JSON) → kb_loader → unified list of (text, metadata)
   - Text strings → OpenAI embeddings API (batched, 100 at a time)
   - Embeddings + metadata → Chroma Cloud upsert (collection: prescribeme_interactions)

2. **Query Flow:**
   - Prescription + patient context → query string
   - Query string → OpenAI embeddings API → query embedding vector
   - Query embedding → Chroma Cloud query (top-k=8, min_relevance_score=0.3)
   - Chroma returns: documents, metadata, distances
   - Distances converted to relevance scores (1 / (1 + distance))
   - Retrieved chunks → LLM with system prompt + evidence block
   - LLM response → assessment text
   - Assessment + retrieved chunks → Frontend

### Environment Variables & Configuration

**Frontend (Vercel):**
- NEXT_PUBLIC_API_URL (Render backend URL)

**Backend (Render):**
- OPENAI_API_KEY (OpenAI API key)
- CHROMA_API_KEY (Chroma Cloud API key)
- CHROMA_TENANT (Chroma Cloud tenant UUID)
- CHROMA_DATABASE (Chroma Cloud database name, e.g. "drugs-database")
- CORS_ORIGINS (comma-separated Vercel frontend URLs)

### Future Enhancements to Show (as dotted/optional boxes)

**Production Readiness:**
- Rate limiting middleware (prevent API abuse)
- Request logging & monitoring (e.g. Sentry, DataDog)
- Response caching (Redis) for common queries
- Structured output (JSON schema) for assessment (risk_level, explanation, alternatives, citations, confidence)
- Evaluation metrics tracking (retrieval precision, LLM response quality)
- A/B testing framework for prompt versions

**Scalability:**
- Load balancer (if multiple Render instances)
- CDN for frontend static assets (Vercel handles this)
- Database connection pooling (Chroma Cloud handles this)
- Async task queue (Celery/RQ) for long-running KB builds
- Webhook notifications for KB build completion

**Security & Compliance:**
- API authentication (JWT tokens or API keys for production)
- Input validation & sanitization (Pydantic models)
- Audit logging (who accessed what, when)
- HIPAA compliance considerations (if handling PHI in future)

**Advanced Features:**
- Multi-language support (i18n)
- Batch analysis endpoint (multiple prescriptions at once)
- Export results (PDF, CSV)
- User accounts & saved prescriptions
- Feedback loop (user corrections → improve KB)

### Visual Style Requirements

- Use clear color coding:
  - Blue: Frontend components
  - Green: Backend API
  - Orange: RAG pipeline modules
  - Purple: External services (Chroma Cloud, OpenAI)
  - Gray: Data sources
  - Yellow: Future enhancements (dotted borders)

- Show data flow with arrows labeled:
  - "HTTP POST" for API calls
  - "Embed" for embedding operations
  - "Query" for vector search
  - "Synthesize" for LLM calls
  - "Store" for database writes

- Group related components:
  - Frontend layer (top)
  - API layer (middle)
  - RAG pipeline layer (middle-bottom)
  - External services (bottom)
  - Data sources (left side)
  - Future enhancements (right side, dotted)

- Include legends:
  - Solid lines: Current implementation
  - Dotted lines: Future enhancements
  - Different arrow styles for different data types (JSON, embeddings, text)

### Key Decision Points to Highlight

1. **Chroma Cloud vs Local:** Show why Chroma Cloud is used (persistence on Render)
2. **Single Collection:** All sources (sample, DrugBank, PubMed) in one collection with source metadata
3. **Strict Grounding:** System prompt enforces "use only retrieved evidence"
4. **Batch Processing:** KB build uses batching (100 docs) for embeddings and upserts
5. **Error Handling:** Show error paths (no retrieval → fallback message, API errors → HTTP 500)

### Additional Notes

- Show the separation between one-time KB build (admin operation) and frequent query operations (user-facing)
- Highlight the RAG pattern: Retrieve → Augment (with context) → Generate
- Include metadata flow: drug_a, drug_b, risk, summary, evidence, alternatives, source, relevance_score
- Show how patient context improves retrieval relevance (combined with prescription in query)
- Indicate where caching could be added (query results, embeddings)

---

**End of Prompt**
