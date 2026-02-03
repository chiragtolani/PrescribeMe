"""Tests for input preprocessing (prescription and patient context)."""
import pytest

from src.preprocessing import (
    preprocess_patient_context,
    preprocess_prescription,
    normalize_text,
)


def test_preprocess_prescription_empty():
    assert preprocess_prescription("") == ""
    assert preprocess_prescription("   ") == ""
    assert preprocess_prescription(None) == ""


def test_preprocess_prescription_normalizes_whitespace():
    assert preprocess_prescription("  Warfarin  5mg  \n  Aspirin  ") == "Warfarin 5mg Aspirin"


def test_preprocess_prescription_truncates():
    long = "A" * 3000
    out = preprocess_prescription(long)
    assert len(out) <= 2003  # MAX_PRESCRIPTION_LENGTH + "..."
    assert out.endswith("...")


def test_preprocess_patient_context_empty():
    assert preprocess_patient_context("") == ""
    assert preprocess_patient_context(None) == ""


def test_preprocess_patient_context_truncates():
    long = "B" * 2000
    out = preprocess_patient_context(long)
    assert len(out) <= 1003
    assert out.endswith("...")


def test_normalize_text_respects_max_length():
    # max_length=5 -> 2 chars + "..." = 5 total
    assert normalize_text("hello world", 5) == "he..."
    assert normalize_text("hi", 10) == "hi"
