"""Tests for RAG pipeline: preprocessing, no-evidence path, and error handling."""
import pytest
from unittest.mock import patch, MagicMock

from src.rag import run_analysis
from src.prompts import FALLBACK_NO_EVIDENCE


def test_run_analysis_empty_prescription():
    out = run_analysis("", "")
    assert out["error"] is None
    assert "at least one drug" in out["assessment"].lower()
    assert out["retrieved"] == []


def test_run_analysis_whitespace_only():
    out = run_analysis("   \n\t  ", "")
    assert out["error"] is None
    assert "at least one drug" in out["assessment"].lower()
    assert out["retrieved"] == []


def test_run_analysis_no_evidence_returns_fallback():
    """When retrieval returns nothing, LLM is not called; fallback message is returned."""
    with patch("src.rag.retrieve_for_prescription", return_value=[]):
        out = run_analysis("UnknownDrugX 100mg", "")
    assert out["error"] is None
    assert out["assessment"] == FALLBACK_NO_EVIDENCE
    assert out["retrieved"] == []


def test_run_analysis_with_retrieved_calls_llm():
    """When retrieval returns chunks, synthesize_assessment is called and result is returned."""
    fake_chunks = [
        {"id": "1", "score": 0.9, "document": "Interaction evidence.", "metadata": {}},
    ]
    fake_assessment = "Risk: moderate. Explanation here."
    with patch("src.rag.retrieve_for_prescription", return_value=fake_chunks), patch(
        "src.rag.synthesize_assessment", return_value=fake_assessment
    ):
        out = run_analysis("Warfarin 5mg", "Patient 70y")
    assert out["error"] is None
    assert out["assessment"] == fake_assessment
    assert out["retrieved"] == fake_chunks


def test_run_analysis_llm_error_returns_error():
    with patch("src.rag.retrieve_for_prescription", return_value=[{"id": "1", "score": 0.8, "document": "x", "metadata": {}}]), patch(
        "src.rag.synthesize_assessment", side_effect=RuntimeError("API down")
    ):
        out = run_analysis("Warfarin", "")
    assert out["error"] == "API down"
    assert out["assessment"] == ""
    assert out["retrieved"] == []


def test_run_analysis_preprocesses_input():
    """Input is preprocessed (e.g. long patient context truncated)."""
    with patch("src.rag.retrieve_for_prescription", return_value=[]) as retrieve:
        run_analysis("  Drug  ", "  context  ")
    retrieve.assert_called_once()
    args = retrieve.call_args[0]
    assert args[0] == "Drug"
    assert args[1] == "context"
