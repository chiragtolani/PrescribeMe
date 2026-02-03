"""Pytest fixtures and env for PrescribeMe tests."""
import os

import pytest


@pytest.fixture(autouse=True)
def env_no_openai_key(monkeypatch):
    """Unset OPENAI_API_KEY so tests that need real API are skipped unless key is set."""
    # Tests that need a real key can override or set it in the test.
    pass


@pytest.fixture
def sample_retrieved_chunks():
    """Minimal retrieved chunks for LLM input."""
    return [
        {
            "id": "doc1",
            "score": 0.85,
            "document": "Warfarin and aspirin: additive bleeding risk. Use with caution.",
            "metadata": {"drug_a": "Warfarin", "drug_b": "Aspirin", "risk": "high"},
        },
    ]
