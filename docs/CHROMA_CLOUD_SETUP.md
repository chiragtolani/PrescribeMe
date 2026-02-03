# Chroma Cloud setup

PrescribeMe can use **Chroma Cloud** as the vector store so the knowledge base persists and is shared across deployments (e.g. Vercel frontend + Render API). This doc covers connecting to Chroma Cloud and importing the KB (sample + PubMed + DrugBank) into it.

---

## 1. Chroma Cloud connection

### Get credentials

1. Sign up at [chroma.cloud](https://chroma.cloud) and create a **tenant** and **database** (e.g. `drugs-database`).
2. From the dashboard, get:
   - **API Key**
   - **Tenant** (UUID, e.g. `f856671c-0f7b-4503-ba4f-02df02c4754b`)
   - **Database** name (e.g. `drugs-database`)

### Set environment variables

**Local (`.env`):**

```bash
CHROMA_API_KEY=your-chroma-cloud-api-key
CHROMA_TENANT=your-tenant-uuid
CHROMA_DATABASE=drugs-database
```

**Production (e.g. Render):** Set the same three variables in your API service’s Environment tab.

When these are set, the app uses `chromadb.CloudClient(api_key=..., tenant=..., database=...)` and all KB operations (build and retrieval) go to Chroma Cloud.

---

## 2. Import PubMed and DrugBank into Chroma Cloud

Import is done by **building the knowledge base** after your data files are ready. The build step reads local JSON files and upserts into Chroma (Cloud or local).

### 2.1 Prepare PubMed data

- **Option A — Script (no API key):**
  ```bash
  cd PrescribeMe
  python -m scripts.fetch_pubmed "drug drug interaction" 50
  ```
  Writes `data/pubmed_abstracts.json`. Change query and count as needed.

- **Option B — Manual:** Create `data/pubmed_abstracts.json` with shape: `[{ "pmid": "...", "title": "...", "abstract": "..." }, ...]`.

### 2.2 Prepare DrugBank data

1. Download DrugBank interaction data (CSV or XML) from [DrugBank](https://go.drugbank.com/).
2. Convert to PrescribeMe format:
   ```bash
   cd PrescribeMe
   python -m scripts.ingest_drugbank path/to/drugbank_export.csv
   ```
   Writes `data/drugbank_interactions.json`. If your CSV columns differ, edit `scripts/ingest_drugbank.py` and set `COLUMN_MAP` to match your export.

### 2.3 Run KB build (import into Chroma Cloud)

With `CHROMA_API_KEY`, `CHROMA_TENANT`, and `CHROMA_DATABASE` set:

- **From the app:** Click **Initialize knowledge base**, or  
- **From CLI:**  
  ```bash
  cd PrescribeMe
  python -m scripts.build_kb
  ```

This loads:

- `data/sample_interactions.json` (always)
- `data/drugbank_interactions.json` (if present)
- `data/pubmed_abstracts.json` (if present)

embeds them with OpenAI, and **upserts into your Chroma Cloud database**. The collection name is `prescribeme_interactions`. Each run **replaces** the existing collection with the current data.

### 2.4 Verify

- Run **Analyze prescription** in the app and confirm you see retrieved evidence.
- In the Chroma Cloud dashboard, check the collection and document count.

---

## 3. Other Chroma modes

- **Self-hosted Chroma server:** Set `CHROMA_HOST` (and optionally `CHROMA_API_KEY`). The app uses `HttpClient` instead of CloudClient. Build step still imports from the same data files into that server.
- **Local (development):** Leave `CHROMA_TENANT` and `CHROMA_HOST` unset. Data is stored in `./chroma_db`. Not suitable for production (ephemeral on Render).

See `src/chroma_store.py` → `get_chroma_client()` for the logic.

---

## 4. Troubleshooting

- **Unauthorized** → Check `CHROMA_API_KEY` and that it’s for the correct tenant.
- **Collection not found / empty** → Run **Initialize knowledge base** (or `python -m scripts.build_kb`) after setting Chroma Cloud env; ensure at least `data/sample_interactions.json` exists.
- **Data missing after deploy** → Confirm Chroma Cloud env vars are set in your deployment (e.g. Render); local Chroma is ephemeral there.

For full KB and data-format details, see [KB_AND_CHROMA.md](KB_AND_CHROMA.md).
