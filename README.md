# PrescribeMe

**Prescription Risk & Drug Interaction Intelligence Agent**

PrescribeMe is an intelligent AI-driven prescription review system designed to identify clinically relevant drug–drug interactions and propose safer, evidence-backed alternatives. Unlike traditional interaction checkers that generate excessive alerts, PrescribeMe uses patient context and medical evidence to prioritize meaningful risks and support safer prescribing decisions.

---

## Features

- **Context-aware drug interaction analysis** — Reviews prescriptions while accounting for patient factors (age, conditions, dosage).
- **Evidence-grounded risk explanations** — Explains interactions using retrieved medical literature and trusted drug knowledge.
- **Safer alternative suggestions** — Proposes clinically reasonable alternatives with supporting evidence when appropriate.
- **Explicit uncertainty signaling** — Clearly flags cases where evidence is weak or insufficient.

---

## Tech stack

| Component        | Technology                          |
|-----------------|--------------------------------------|
| **UI**          | **Next.js 14** (App Router), Tailwind CSS, Framer Motion, Lucide icons |
| **API**         | **FastAPI** (CORS for frontend)     |
| Backend / RAG   | **Python** (Retrieval-Augmented Generation) |
| Embeddings      | **OpenAI text-embedding-3-small**    |
| Vector store    | **Chroma** (local or cloud) or Pinecone |
| LLM             | **OpenAI** (e.g. gpt-4o-mini)        |
| Data sources    | Sample interactions (in repo) + **DrugBank** + **PubMed** (see [KB setup](docs/KB_AND_CHROMA.md)) |

*(Optional: Streamlit UI via `streamlit run app.py`.)*

---

## Setup

### 1. Backend (Python)

1. **Clone and enter the project**
   ```bash
   git clone <repo-url> PrescribeMe
   cd PrescribeMe
   ```
   **Large files (DrugBank):** This repo uses [Git LFS](https://git-lfs.github.com/) for `drugbank.xml` and `data/drugbank_interactions.json`. After cloning, run `git lfs pull` (or ensure Git LFS is installed and fetch will pull LFS files automatically).

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   - Copy `.env.example` to `.env`
   - Set your OpenAI API key: `OPENAI_API_KEY=sk-your-key`

5. **Start the API**
   ```bash
   uvicorn api.main:app --reload --port 8000
   ```
   *(Run from project root so `config` and `src` resolve.)*

### 2. Frontend (Next.js)

1. **Enter frontend and install**
   ```bash
   cd frontend
   npm install
   ```

2. **Optional:** Copy `frontend/.env.local.example` to `frontend/.env.local` and set `NEXT_PUBLIC_API_URL=http://localhost:8000` if your API runs elsewhere.

3. **Start the dev server**
   ```bash
   npm run dev
   ```
   Open [http://localhost:3000](http://localhost:3000).

### 3. First run

- In the sidebar, click **Initialize knowledge base** once to load sample drug interaction data into Chroma.
- Enter prescription text (e.g. drug names) and click **Analyze prescription**.

---

## Deploy (Vercel + Render)

To get a **hosted URL**:

- **Frontend** → [Vercel](https://vercel.com): connect repo, set **Root Directory** to `frontend`, add env `NEXT_PUBLIC_API_URL` (your backend URL).
- **Backend** → [Render](https://render.com): deploy as a Web Service from repo root; set `OPENAI_API_KEY` and `CORS_ORIGINS` (your Vercel URL).

See **[DEPLOYMENT.md](./DEPLOYMENT.md)** for step-by-step instructions and env details.

**Note:** For production (Vercel/Render), use **Chroma Cloud** (set `CHROMA_HOST` + `CHROMA_API_KEY`) instead of local Chroma. See **[docs/CHROMA_CLOUD_SETUP.md](./docs/CHROMA_CLOUD_SETUP.md)**.

---

## Project structure

```
PrescribeMe/
├── api/
│   └── main.py           # FastAPI app (analyze, init-kb, health)
├── app.py                # Streamlit entrypoint (optional)
├── config.py             # Configuration (paths, OpenAI, Chroma, RAG)
├── requirements.txt
├── .env.example
├── data/
│   └── sample_interactions.json
├── src/
│   ├── embeddings.py
│   ├── chroma_store.py
│   ├── retrieval.py
│   ├── llm.py
│   ├── rag.py
│   ├── prompts.py        # LLM prompt templates (tune here)
│   └── preprocessing.py  # Input normalization and length limits
├── tests/                # Pytest: preprocessing, RAG, LLM, API
├── frontend/             # Next.js app
│   ├── app/              # App Router (layout, page, globals.css)
│   ├── components/       # Header, PatientContext, PrescriptionForm, Results, EvidenceCard, InitKB
│   ├── lib/              # api.ts (fetch to backend)
│   └── package.json
└── chroma_db/            # Created at runtime (Chroma persistence)
```

---

## Testing

From the project root:

```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```

Tests cover input preprocessing, RAG flow (with mocked LLM), response parsing, API validation, and cache behavior. Backend tests do not require a live OpenAI or Chroma instance except where noted.

---

## Disclaimer

PrescribeMe is intended as a **decision-support tool**, not a replacement for clinical judgement. The project prioritizes transparency, safety, and explainability. Always verify with authoritative drug references and clinical guidelines.
