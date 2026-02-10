"""
PrescribeMe FastAPI backend — used by the Next.js frontend.
Run from project root: uvicorn api.main:app --reload --port 8000
"""
import hashlib
import os
from typing import Any, Callable

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.middleware.base import BaseHTTPMiddleware

from config import (
    CHROMA_COLLECTION_NAME,
    MAX_PATIENT_CONTEXT_LENGTH,
    MAX_PRESCRIPTION_LENGTH,
)
from src.chroma_store import build_knowledge_base, get_chroma_client
from src.rag import run_analysis

app = FastAPI(
    title="PrescribeMe API",
    description="Prescription Risk & Drug Interaction Intelligence",
    version="1.0.0",
)

# CORS: allow frontend origin. In production (e.g. Render) set CORS_ORIGINS to your Vercel URL.
# Example: CORS_ORIGINS=https://prescribe-me.vercel.app (comma-separated for multiple)
_default_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]
_cors_origins = os.getenv("CORS_ORIGINS", "").strip()
_origins_list = [o.strip().rstrip("/") for o in _cors_origins.split(",") if o.strip()]
# Include both with and without trailing slash so browser Origin always matches
allow_origins = _origins_list or _default_origins
allow_origins = list(dict.fromkeys(allow_origins + [o + "/" for o in allow_origins]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)


class EnsureCORSHeadersMiddleware(BaseHTTPMiddleware):
    """Ensure CORS headers are on every response (e.g. 404 from our app)."""

    async def dispatch(self, request: Request, call_next: Callable):
        response = await call_next(request)
        origin = request.headers.get("origin")
        if origin and origin in allow_origins:
            response.headers.setdefault("access-control-allow-origin", origin)
            response.headers.setdefault("access-control-allow-credentials", "true")
        return response


app.add_middleware(EnsureCORSHeadersMiddleware)


@app.on_event("startup")
def _log_cors():
    import sys
    print("CORS allowed origins:", allow_origins, file=sys.stderr)

# Optional in-memory cache for analyze (avoids duplicate LLM calls). Disable with ENABLE_ANALYZE_CACHE=0.
_enable_cache = os.getenv("ENABLE_ANALYZE_CACHE", "1").strip().lower() in ("1", "true", "yes")
_analyze_cache: dict[str, dict[str, Any]] = {}
_CACHE_MAX_ENTRIES = int(os.getenv("ANALYZE_CACHE_MAX_ENTRIES", "100"))


def _cache_key(prescription: str, patient_context: str) -> str:
    return hashlib.sha256((prescription.strip() + "\0" + (patient_context or "").strip()).encode()).hexdigest()


class AnalyzeRequest(BaseModel):
    prescription_text: str = Field(..., min_length=1, max_length=MAX_PRESCRIPTION_LENGTH + 500)
    patient_context: str = Field(default="", max_length=MAX_PATIENT_CONTEXT_LENGTH + 500)


class InitKBResponse(BaseModel):
    ok: bool
    message: str
    count: int | None = None


@app.post("/api/analyze")
def analyze(request: AnalyzeRequest):
    """Run RAG analysis on prescription text with optional patient context.
    Validates input length; optionally returns cached result for identical request.
    """
    prescription = (request.prescription_text or "").strip()
    patient_context = (request.patient_context or "").strip()
    if not prescription:
        raise HTTPException(status_code=400, detail="prescription_text is required and cannot be empty.")

    key = _cache_key(prescription, patient_context)
    if _enable_cache and key in _analyze_cache:
        return _analyze_cache[key]
    if _enable_cache:
        while len(_analyze_cache) >= _CACHE_MAX_ENTRIES:
            _analyze_cache.pop(next(iter(_analyze_cache)))

    result = run_analysis(
        prescription_text=prescription,
        patient_context=patient_context,
    )
    if result["error"]:
        raise HTTPException(status_code=500, detail=result["error"])

    out = {
        "assessment": result["assessment"],
        "retrieved": result["retrieved"],
    }
    if _enable_cache:
        _analyze_cache[key] = out
    return out


@app.post("/api/init-kb")
def init_knowledge_base():
    """Initialize Chroma from sample + DrugBank + PubMed data. Replaces existing KB."""
    try:
        count = build_knowledge_base(clear_first=True)
        return InitKBResponse(ok=True, message="Knowledge base ready.", count=count)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
def health():
    """Health check. Includes allowed CORS origins for debugging."""
    normalized = list(dict.fromkeys(o.rstrip("/") for o in allow_origins))
    return {"status": "ok", "cors_allowed_origins": normalized}
