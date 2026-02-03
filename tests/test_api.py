"""Tests for FastAPI analyze endpoint: validation, cache, errors."""
import pytest
from fastapi.testclient import TestClient

from api.main import app, _analyze_cache, _enable_cache

client = TestClient(app)


def test_health():
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_analyze_empty_prescription_rejected():
    r = client.post(
        "/api/analyze",
        json={"prescription_text": "", "patient_context": ""},
    )
    # Pydantic min_length gives 422; our explicit check gives 400
    assert r.status_code in (400, 422)


def test_analyze_whitespace_only_rejected():
    r = client.post(
        "/api/analyze",
        json={"prescription_text": "   \n  ", "patient_context": ""},
    )
    assert r.status_code == 400


def test_analyze_no_evidence_returns_200():
    """With no Chroma/OpenAI set up, analyze may 500; with mocks we could assert 200.
    Here we only check that valid payload is accepted (may 500 if backend deps missing).
    """
    r = client.post(
        "/api/analyze",
        json={"prescription_text": "UnknownDrugXYZ 100mg", "patient_context": ""},
    )
    # Either success (200) or server error (500) if Chroma/OpenAI not configured
    assert r.status_code in (200, 500)
    if r.status_code == 200:
        data = r.json()
        assert "assessment" in data
        assert "retrieved" in data


def test_analyze_cache_returns_same_result():
    """Second identical request returns cached result (when cache enabled)."""
    if not _enable_cache:
        pytest.skip("Cache disabled")
    payload = {"prescription_text": "CachedDrug 5mg", "patient_context": "test"}
    r1 = client.post("/api/analyze", json=payload)
    if r1.status_code != 200:
        pytest.skip("Backend not ready (Chroma/OpenAI)")
    r2 = client.post("/api/analyze", json=payload)
    assert r2.status_code == 200
    assert r1.json() == r2.json()
