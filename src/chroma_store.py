"""Chroma vector store for interaction documents."""
import json
from pathlib import Path

import chromadb
from chromadb.config import Settings

from config import CHROMA_COLLECTION_NAME, CHROMA_PERSIST_DIR, DATA_DIR
from src.embeddings import embed_texts, get_client


def get_chroma_client():
    return chromadb.PersistentClient(
        path=CHROMA_PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False),
    )


def _document_to_text(doc: dict) -> str:
    """Build searchable text from an interaction document."""
    return (
        f"Drug interaction: {doc.get('drug_a', '')} and {doc.get('drug_b', '')}. "
        f"Risk: {doc.get('risk', '')}. "
        f"{doc.get('summary', '')} "
        f"Evidence: {doc.get('evidence', '')} "
        f"Alternatives: {doc.get('alternatives', '')}"
    )


def build_and_populate_store(openai_client=None, chroma_client=None):
    """Load sample interactions, embed, and upsert into Chroma. Idempotent."""
    data_path = DATA_DIR / "sample_interactions.json"
    if not data_path.exists():
        raise FileNotFoundError(f"Sample data not found: {data_path}")

    with open(data_path, encoding="utf-8") as f:
        docs = json.load(f)

    if not docs:
        return

    openai_client = openai_client or get_client()
    chroma_client = chroma_client or get_chroma_client()
    collection = chroma_client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME,
        metadata={"description": "PrescribeMe drug interaction evidence"},
    )

    texts = [_document_to_text(d) for d in docs]
    ids = [f"int_{i}" for i in range(len(docs))]
    embeddings = embed_texts(openai_client, texts)

    metadatas = [
        {
            "drug_a": d.get("drug_a", ""),
            "drug_b": d.get("drug_b", ""),
            "risk": d.get("risk", ""),
            "summary": d.get("summary", ""),
            "evidence": d.get("evidence", ""),
            "alternatives": d.get("alternatives", ""),
            "confidence": d.get("confidence", ""),
        }
        for d in docs
    ]
    collection.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
    return len(docs)
