"""
Load KB documents from sample_interactions.json, drugbank_interactions.json, and pubmed_abstracts.json.
Returns a unified list of {text, metadata} for Chroma upsert.
"""
import json
from pathlib import Path

from config import DATA_DIR

# Metadata keys Chroma accepts: str, int, float, bool. We use str for all.
SOURCE_SAMPLE = "sample"
SOURCE_DRUGBANK = "drugbank"
SOURCE_PUBMED = "pubmed"


def _doc_to_text(doc: dict, source: str) -> str:
    """Build searchable text from a doc. Used for both interaction-style and PubMed-style."""
    if source == SOURCE_PUBMED:
        title = doc.get("title", "")
        abstract = doc.get("abstract", "")
        return f"PubMed: {title}. {abstract}".strip()
    # Interaction-style (sample, drugbank)
    return (
        f"Drug interaction: {doc.get('drug_a', '')} and {doc.get('drug_b', '')}. "
        f"Risk: {doc.get('risk', '')}. "
        f"{doc.get('summary', '')} "
        f"Evidence: {doc.get('evidence', '')} "
        f"Alternatives: {doc.get('alternatives', '')}"
    )


def _interaction_metadata(doc: dict, source: str) -> dict:
    """Metadata for Chroma (all values str)."""
    return {
        "drug_a": str(doc.get("drug_a", "")),
        "drug_b": str(doc.get("drug_b", "")),
        "risk": str(doc.get("risk", "")),
        "summary": str(doc.get("summary", "")),
        "evidence": str(doc.get("evidence", "")),
        "alternatives": str(doc.get("alternatives", "")),
        "confidence": str(doc.get("confidence", "")),
        "source": source,
    }


def _pubmed_metadata(doc: dict) -> dict:
    """Metadata for PubMed chunks (drug_a/drug_b empty)."""
    return {
        "drug_a": "",
        "drug_b": "",
        "risk": "",
        "summary": str(doc.get("title", ""))[:2000],
        "evidence": str(doc.get("abstract", ""))[:4000],
        "alternatives": "",
        "confidence": "",
        "source": SOURCE_PUBMED,
        "pmid": str(doc.get("pmid", "")),
    }


def load_sample() -> list[tuple[str, dict]]:
    """Load data/sample_interactions.json. Returns list of (text, metadata)."""
    path = DATA_DIR / "sample_interactions.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        docs = json.load(f)
    if not isinstance(docs, list):
        return []
    out = []
    for d in docs:
        text = _doc_to_text(d, SOURCE_SAMPLE)
        meta = _interaction_metadata(d, SOURCE_SAMPLE)
        out.append((text, meta))
    return out


def load_drugbank() -> list[tuple[str, dict]]:
    """Load data/drugbank_interactions.json. Same schema as sample (drug_a, drug_b, risk, summary, evidence, alternatives, confidence)."""
    path = DATA_DIR / "drugbank_interactions.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        docs = json.load(f)
    if not isinstance(docs, list):
        return []
    out = []
    for d in docs:
        text = _doc_to_text(d, SOURCE_DRUGBANK)
        meta = _interaction_metadata(d, SOURCE_DRUGBANK)
        out.append((text, meta))
    return out


def load_pubmed() -> list[tuple[str, dict]]:
    """Load data/pubmed_abstracts.json. Expects [{pmid, title, abstract}, ...]."""
    path = DATA_DIR / "pubmed_abstracts.json"
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        docs = json.load(f)
    if not isinstance(docs, list):
        return []
    out = []
    for d in docs:
        if not d.get("title") and not d.get("abstract"):
            continue
        text = _doc_to_text(d, SOURCE_PUBMED)
        meta = _pubmed_metadata(d)
        out.append((text, meta))
    return out


def load_all_documents() -> list[tuple[str, dict]]:
    """Load sample + drugbank + pubmed and return unified list of (text, metadata)."""
    all_docs: list[tuple[str, dict]] = []
    all_docs.extend(load_sample())
    all_docs.extend(load_drugbank())
    all_docs.extend(load_pubmed())
    return all_docs
