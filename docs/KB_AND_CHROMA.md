# Chroma RAG Knowledge Base

This doc describes how the RAG knowledge base works, how to use **Chroma Cloud** as the vector store, and how to **import PubMed and DrugBank** datasets into Chroma.

---

## Chroma as the RAG vector database

### What’s implemented

| Component | Implementation |
|-----------|----------------|
| **Vector store** | **Chroma** — local (on-disk) or **Chroma Cloud** (recommended for production) |
| **Connection** | `CloudClient` when `CHROMA_TENANT` + `CHROMA_API_KEY` are set; else `PersistentClient` (local) or `HttpClient` (self-hosted server) |
| **Collection** | Single collection: `prescribeme_interactions` (name from `config.CHROMA_COLLECTION_NAME`) |
| **Embeddings** | OpenAI `text-embedding-3-small` |
| **Indexing** | Each document is one chunk: full interaction or abstract text, embedded once and stored with metadata |

### End-to-end flow

1. **Prepare data** (see [Import PubMed and DrugBank](#import-pubmed-and-drugbank-into-chroma-cloud))  
   - Sample: `data/sample_interactions.json` (shipped).  
   - DrugBank: produce `data/drugbank_interactions.json` (e.g. via `scripts.ingest_drugbank`).  
   - PubMed: produce `data/pubmed_abstracts.json` (e.g. via `scripts.fetch_pubmed`).

2. **Set environment**  
   - `OPENAI_API_KEY` (required for embeddings).  
   - For **Chroma Cloud**: `CHROMA_API_KEY`, `CHROMA_TENANT`, `CHROMA_DATABASE` (see [docs/CHROMA_CLOUD_SETUP.md](CHROMA_CLOUD_SETUP.md)).

3. **Build KB (import into Chroma)**  
   - **From UI:** Click **Initialize knowledge base** in the app (calls `POST /api/init-kb`).  
   - **From CLI:** From project root, run `python -m scripts.build_kb`.  
   - The script loads all documents from the three data sources, embeds them, and **upserts into Chroma** (local or Chroma Cloud, depending on env). Each run **replaces** the existing collection with the current data.

4. **Retrieval**  
   - Prescription + patient context → embedded query → Chroma returns top-k similar chunks → LLM synthesizes assessment from that evidence.

---

## Import PubMed and DrugBank into Chroma Cloud

You don’t “import” directly into Chroma Cloud by hand. You **prepare local data files**, then run the **KB build** once. The build step reads those files and pushes everything into Chroma (Cloud or local).

### Step 1: Chroma Cloud credentials

In `.env` (and in your deployment env, e.g. Render):

```bash
CHROMA_API_KEY=your-chroma-cloud-api-key
CHROMA_TENANT=your-tenant-uuid
CHROMA_DATABASE=drugs-database
```

See [CHROMA_CLOUD_SETUP.md](CHROMA_CLOUD_SETUP.md) for details.

### Step 2: PubMed data → Chroma Cloud

1. **Create PubMed data file** (one of these):
   - **Option A — Fetch via script (recommended):**
     ```bash
     cd PrescribeMe
     python -m scripts.fetch_pubmed "drug drug interaction" 50
     ```
     This writes `data/pubmed_abstracts.json`. You can change the query and max results.
   - **Option B — Manual:** Create `data/pubmed_abstracts.json` as a JSON array of `{ "pmid": "...", "title": "...", "abstract": "..." }`.

2. **Import into Chroma Cloud:**  
   Run the KB build (Step 4 below). It will include PubMed (and sample + DrugBank if present).

### Step 3: DrugBank data → Chroma Cloud

1. **Get DrugBank data**  
   - Register at [DrugBank](https://go.drugbank.com/) and download the release that includes drug–drug interactions (CSV or XML).

2. **Convert to PrescribeMe format**  
   - From project root:
     ```bash
     python -m scripts.ingest_drugbank path/to/your_drugbank_export.csv
     ```
   - This produces `data/drugbank_interactions.json`.  
   - If your CSV has different column names, edit `scripts/ingest_drugbank.py` and set `COLUMN_MAP` to match your export (e.g. `drug1`/`drug2`, `severity`, `description`).  
   - For XML or other formats, adapt the script or write a small converter that outputs the same JSON schema (see [Data formats](#data-formats)).

3. **Import into Chroma Cloud:**  
   Run the KB build (Step 4 below). It will include DrugBank (and sample + PubMed if present).

### Step 4: Run KB build (push to Chroma Cloud)

With `CHROMA_*` set and your data files in place:

- **From the app:** Click **Initialize knowledge base**.  
- **From CLI:**  
  ```bash
  cd PrescribeMe
  python -m scripts.build_kb
  ```

This loads `data/sample_interactions.json`, `data/drugbank_interactions.json` (if present), and `data/pubmed_abstracts.json` (if present), embeds them with OpenAI, and **upserts into your Chroma Cloud database** (same collection name: `prescribeme_interactions`). Existing documents in that collection are replaced.

### Step 5: Verify

- In the app, run **Analyze prescription** with a few drug names; you should see retrieved evidence and an assessment.  
- In Chroma Cloud dashboard you can confirm the collection and document count.

---

## Data formats

### Sample interactions

- **File:** `data/sample_interactions.json` (shipped in repo)
- **Shape:** JSON array of objects with: `drug_a`, `drug_b`, `risk`, `summary`, `evidence`, `alternatives`, `confidence`  
- Loader tags them as `source: "sample"`.

### DrugBank interaction data

- **File:** `data/drugbank_interactions.json`
- **Shape:** Same as sample: `drug_a`, `drug_b`, `risk`, `summary`, `evidence`, `alternatives`, `confidence` (all strings). Loader tags as `source: "drugbank"`.
- Use `scripts.ingest_drugbank` to convert a DrugBank CSV (or adapt for XML) into this file.

### PubMed abstracts

- **File:** `data/pubmed_abstracts.json`
- **Shape:** JSON array of objects with at least: `pmid`, `title`, `abstract`. Loader uses `title` + `abstract` as searchable text and tags as `source: "pubmed"`; `drug_a`/`drug_b` are left empty.

---

## Code locations

- **Chroma client** — `src/chroma_store.py`: `get_chroma_client()` (CloudClient when `CHROMA_TENANT` + `CHROMA_API_KEY` set), `build_knowledge_base()`.
- **Document loading** — `src/kb_loader.py`: `load_sample()`, `load_drugbank()`, `load_pubmed()`, `load_all_documents()`.
- **Embeddings** — `src/embeddings.py`: `embed_texts()`, `embed_single()` (OpenAI).
- **Retrieval** — `src/retrieval.py`: `retrieve_for_prescription()`.
- **Config** — `config.py`: `CHROMA_*`, `CHROMA_COLLECTION_NAME`, `TOP_K_RETRIEVAL`, `MIN_RELEVANCE_SCORE`, `EMBEDDING_MODEL`.

---

## Summary checklist

- [ ] Chroma Cloud env set: `CHROMA_API_KEY`, `CHROMA_TENANT`, `CHROMA_DATABASE` (see [CHROMA_CLOUD_SETUP.md](CHROMA_CLOUD_SETUP.md)).
- [ ] `OPENAI_API_KEY` set (required for embeddings).
- [ ] Sample data present: `data/sample_interactions.json`.
- [ ] (Optional) PubMed: run `python -m scripts.fetch_pubmed ...` or add `data/pubmed_abstracts.json`.
- [ ] (Optional) DrugBank: run `python -m scripts.ingest_drugbank <csv>` to create `data/drugbank_interactions.json`.
- [ ] Run KB build: **Initialize knowledge base** in app or `python -m scripts.build_kb` → data is imported into Chroma Cloud.
- [ ] Verify with **Analyze prescription** and/or Chroma Cloud dashboard.

After this, the RAG knowledge base is stored in Chroma Cloud and used for every analysis.
