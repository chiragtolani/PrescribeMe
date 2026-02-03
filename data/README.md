# RAG Knowledge Base data

This folder holds the **source data** for the PrescribeMe RAG knowledge base. The app does **not** read these files at query time. Instead, you run a **KB build** (Initialize knowledge base in the app or `python -m scripts.build_kb`), which:

1. Reads the JSON files from this folder  
2. Embeds them with OpenAI  
3. **Imports them into Chroma** — either **Chroma Cloud** (when `CHROMA_API_KEY`, `CHROMA_TENANT`, `CHROMA_DATABASE` are set) or local `./chroma_db`

So: add or update files here, then run the KB build to push the latest data into Chroma (local or Cloud).

---

## Files

| File | Required | Description |
|------|----------|-------------|
| `sample_interactions.json` | Yes (shipped) | Curated sample drug–drug interactions. |
| `drugbank_interactions.json` | Optional | DrugBank-style interactions. Create via `scripts.ingest_drugbank` (see below). |
| `pubmed_abstracts.json` | Optional | PubMed abstracts. Create via `scripts.fetch_pubmed` or manually. |

After adding or changing any file, run **Initialize knowledge base** in the app or `python -m scripts.build_kb` to **re-import into Chroma** (existing collection is replaced).

---

## sample_interactions.json

Already in the repo. Array of objects:

- `drug_a`, `drug_b` — string  
- `risk` — string (e.g. `high`, `moderate`, `low`)  
- `summary`, `evidence`, `alternatives` — string  
- `confidence` — string (optional)

---

## drugbank_interactions.json (DrugBank)

Same schema as `sample_interactions.json`: `drug_a`, `drug_b`, `risk`, `summary`, `evidence`, `alternatives`, `confidence`.

**How to create:**

1. Download DrugBank interaction data (CSV or XML) from [DrugBank](https://go.drugbank.com/).
2. From project root:
   ```bash
   python -m scripts.ingest_drugbank path/to/drugbank_export.csv
   ```
   This writes `data/drugbank_interactions.json`. If your CSV uses different column names, edit `scripts/ingest_drugbank.py` and set `COLUMN_MAP` to match. For XML, adapt the script or build a small converter that outputs this JSON shape.

Then run **Initialize knowledge base** (or `python -m scripts.build_kb`) to import into Chroma (local or Chroma Cloud).

---

## pubmed_abstracts.json (PubMed)

Array of objects with at least: `pmid`, `title`, `abstract`.

**How to create:**

- **Script (recommended):**  
  ```bash
  python -m scripts.fetch_pubmed "drug drug interaction" 50
  ```  
  Writes `data/pubmed_abstracts.json`. You can change the query and max results.

- **Manual:** Create `data/pubmed_abstracts.json` with shape: `[{ "pmid": "...", "title": "...", "abstract": "..." }, ...]`.

Then run **Initialize knowledge base** (or `python -m scripts.build_kb`) to import into Chroma (local or Chroma Cloud).

---

## Chroma Cloud vs local

- **Chroma Cloud:** Set `CHROMA_API_KEY`, `CHROMA_TENANT`, `CHROMA_DATABASE` in `.env` (and in your deployment). The KB build imports into your Chroma Cloud database. See [docs/CHROMA_CLOUD_SETUP.md](../docs/CHROMA_CLOUD_SETUP.md).
- **Local:** Leave those unset. The KB is stored in `./chroma_db` (good for dev only; not persistent on platforms like Render).

Full flow and data formats: [docs/KB_AND_CHROMA.md](../docs/KB_AND_CHROMA.md).
