"""Tests for LLM module: response parsing, fallbacks, retries (mocked API)."""
import pytest
from unittest.mock import patch, MagicMock

from src.llm import synthesize_assessment, _postprocess_response
from src.prompts import FALLBACK_NO_EVIDENCE, FALLBACK_NO_RESPONSE


def test_synthesize_no_chunks_returns_fallback():
    assert synthesize_assessment("Warfarin", "", []) == FALLBACK_NO_EVIDENCE


def test_postprocess_response_empty():
    assert _postprocess_response(None) == FALLBACK_NO_RESPONSE
    assert _postprocess_response("") == FALLBACK_NO_RESPONSE
    assert _postprocess_response("   ") == FALLBACK_NO_RESPONSE


def test_postprocess_response_truncates_very_long():
    long_text = "A" * 12000
    out = _postprocess_response(long_text)
    assert len(out) <= 8000
    assert "[Response truncated." in out


@patch("src.llm.get_llm_client")
def test_synthesize_returns_postprocessed_content(mock_client):
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = " Risk: high. See [Source 1]. "
    mock_client.return_value.chat.completions.create.return_value = mock_resp

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        out = synthesize_assessment(
            "Warfarin, Aspirin",
            "",
            [{"id": "1", "score": 0.9, "document": "Evidence.", "metadata": {}}],
        )
    assert out.strip() == "Risk: high. See [Source 1]."


@patch("src.llm.get_llm_client")
def test_synthesize_handles_empty_choice_content(mock_client):
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock()]
    mock_resp.choices[0].message.content = None
    mock_client.return_value.chat.completions.create.return_value = mock_resp

    with patch.dict("os.environ", {"OPENAI_API_KEY": "sk-test"}):
        out = synthesize_assessment(
            "Warfarin",
            "",
            [{"id": "1", "score": 0.9, "document": "Evidence.", "metadata": {}}],
        )
    assert out == FALLBACK_NO_RESPONSE
