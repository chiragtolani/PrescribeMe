"""
PrescribeMe FastAPI backend — used by the Next.js frontend.
Run from project root: uvicorn api.main:app --reload --port 8000
"""
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import CHROMA_COLLECTION_NAME
from src.chroma_store import build_and_populate_store, get_chroma_client
from src.rag import run_analysis

app = FastAPI(
    title="PrescribeMe API",
    description="Prescription Risk & Drug Interaction Intelligence",
    version="1.0.0",
)

# CORS: allow Vercel frontend and localhost. Set CORS_ORIGINS in production (comma-separated).
_default_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
_cors_origins = os.getenv("CORS_ORIGINS", "").strip()
allow_origins = [o.strip() for o in _cors_origins.split(",") if o.strip()] or _default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    prescription_text: str
    patient_context: str = ""


class InitKBResponse(BaseModel):
    ok: bool
    message: str
    count: int | None = None


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest):
    """Run RAG analysis on prescription text with optional patient context."""
    result = run_analysis(
        prescription_text=request.prescription_text,
        patient_context=request.patient_context,
    )
    if result["error"]:
        raise HTTPException(status_code=500, detail=result["error"])
    return {
        "assessment": result["assessment"],
        "retrieved": result["retrieved"],
    }


@app.post("/api/init-kb")
def init_knowledge_base():
    """Initialize Chroma with sample drug interaction data. Idempotent."""
    try:
        client = get_chroma_client()
        coll = client.get_or_create_collection(
            name=CHROMA_COLLECTION_NAME,
            metadata={"description": "PrescribeMe drug interaction evidence"},
        )
        if coll.count() > 0:
            return InitKBResponse(ok=True, message="Knowledge base already populated.", count=coll.count())
        count = build_and_populate_store()
        return InitKBResponse(ok=True, message="Knowledge base ready.", count=count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
def health():
    return {"status": "ok"}
