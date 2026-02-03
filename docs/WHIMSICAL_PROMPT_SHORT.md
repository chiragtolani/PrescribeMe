# Whimsical Prompt (Short Version - Copy This)

Create a production-ready application architecture flowchart for PrescribeMe, a RAG-based prescription risk analysis system.

**Architecture:** Next.js frontend (Vercel) → FastAPI backend (Render) → Chroma Cloud (vector DB) + OpenAI (embeddings + LLM)

**Show these flows:**

1. **KB Initialization:** User clicks "Initialize KB" → Frontend POST /api/init-kb → Backend loads sample_interactions.json + drugbank_interactions.json + pubmed_abstracts.json → Each doc embedded (OpenAI text-embedding-3-small) → Upserted to Chroma Cloud collection "prescribeme_interactions" → Returns count

2. **Prescription Analysis:** User enters prescription + patient context → Frontend POST /api/analyze → Backend combines into query → Query embedded → Chroma Cloud queried (top-8) → Retrieved chunks passed to LLM (gpt-4o-mini) with system prompt enforcing strict grounding → LLM synthesizes assessment → Response (assessment + retrieved chunks with relevance scores) → Frontend displays assessment + expandable evidence cards

**Components to include:**

**Frontend (Next.js/Vercel):** Header, PatientContext sidebar, PrescriptionForm, Results, EvidenceCard (expandable), InitKB, API client (lib/api.ts)

**Backend (FastAPI/Render):** POST /api/analyze, POST /api/init-kb, GET /api/health, CORS middleware

**RAG Pipeline:** src/rag.py (orchestrator), src/retrieval.py (Chroma query), src/llm.py (synthesis), src/embeddings.py (OpenAI), src/chroma_store.py (KB build), src/kb_loader.py (data loading)

**External:** Chroma Cloud (CloudClient), OpenAI API (embeddings + LLM)

**Data:** sample_interactions.json, drugbank_interactions.json, pubmed_abstracts.json

**Scripts:** fetch_pubmed.py (NCBI API → JSON), ingest_drugbank.py (CSV → JSON), build_kb.py (populate Chroma)

**Future enhancements (dotted boxes):** Rate limiting, monitoring/logging, Redis caching, structured JSON output, evaluation metrics, async task queue, API auth, batch analysis, user accounts

**Visual:** Color-code layers (Frontend=Blue, Backend=Green, RAG=Orange, External=Purple, Data=Gray, Future=Yellow dotted). Show data flows with labeled arrows (HTTP POST, Embed, Query, Synthesize, Store). Group by layer. Include legends for current vs future.

**Key decisions:** Chroma Cloud for persistence, single collection with source metadata, strict grounding via system prompt, batch processing (100 docs), error handling paths.
