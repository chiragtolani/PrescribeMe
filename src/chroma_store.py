"""Chroma vector store for interaction documents and RAG knowledge base."""
import chromadb
from chromadb.config import Settings

from config import (
    CHROMA_COLLECTION_NAME,
    CHROMA_PERSIST_DIR,
    CHROMA_HOST,
    CHROMA_API_KEY,
    CHROMA_TENANT,
    CHROMA_DATABASE,
)
from src.embeddings import embed_texts, get_client
from src.kb_loader import load_all_documents

# Batch size for OpenAI embeddings and Chroma upsert (avoid rate limits and payload size)
KB_BATCH_SIZE = 100


def get_chroma_client():
    """
    Get Chroma client:
    - CloudClient if CHROMA_TENANT (and CHROMA_API_KEY) set (Chroma Cloud)
    - HttpClient if CHROMA_HOST set (self-hosted HTTP server)
    - PersistentClient otherwise (local on-disk)
    """
    if CHROMA_TENANT and CHROMA_API_KEY:
        return chromadb.CloudClient(
            api_key=CHROMA_API_KEY,
            tenant=CHROMA_TENANT,
            database=CHROMA_DATABASE,
        )
    if CHROMA_HOST:
        if CHROMA_API_KEY:
            return chromadb.HttpClient(host=CHROMA_HOST, api_key=CHROMA_API_KEY)
        return chromadb.HttpClient(host=CHROMA_HOST)
    return chromadb.PersistentClient(
        path=CHROMA_PERSIST_DIR,
        settings=Settings(anonymized_telemetry=False),
    )


def build_knowledge_base(openai_client=None, chroma_client=None, *, clear_first: bool = True):
    """
    Load all KB documents (sample + drugbank + pubmed), embed, and upsert into Chroma.
    Idempotent if you do not clear_first; set clear_first=True to replace existing KB.
    Returns total number of documents added.
    """
    all_docs = load_all_documents()
    if not all_docs:
        raise FileNotFoundError(
            "No KB documents found. Ensure at least one of: "
            "data/sample_interactions.json, data/drugbank_interactions.json, data/pubmed_abstracts.json exists."
        )

    openai_client = openai_client or get_client()
    chroma_client = chroma_client or get_chroma_client()
    collection = chroma_client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME,
        metadata={"description": "PrescribeMe drug interaction evidence"},
    )

    if clear_first:
        existing = collection.get(include=[])
        if existing and existing.get("ids"):
            collection.delete(ids=existing["ids"])

    texts = [t for t, _ in all_docs]
    metadatas = [m for _, m in all_docs]
    ids = [f"{m.get('source', 'doc')}_{i}" for i, (_, m) in enumerate(all_docs)]

    total = 0
    for i in range(0, len(texts), KB_BATCH_SIZE):
        batch_texts = texts[i : i + KB_BATCH_SIZE]
        batch_ids = ids[i : i + KB_BATCH_SIZE]
        batch_metadatas = metadatas[i : i + KB_BATCH_SIZE]
        batch_embeddings = embed_texts(openai_client, batch_texts)
        collection.upsert(
            ids=batch_ids,
            documents=batch_texts,
            embeddings=batch_embeddings,
            metadatas=batch_metadatas,
        )
        total += len(batch_ids)

    return total


def build_and_populate_store(openai_client=None, chroma_client=None):
    """
    Legacy: load only data/sample_interactions.json and populate Chroma.
    Prefer build_knowledge_base() for sample + DrugBank + PubMed.
    """
    from pathlib import Path

    import json

    from config import DATA_DIR

    data_path = DATA_DIR / "sample_interactions.json"
    if not data_path.exists():
        raise FileNotFoundError(f"Sample data not found: {data_path}")

    with open(data_path, encoding="utf-8") as f:
        docs = json.load(f)

    if not docs:
        return 0

    def _doc_to_text(d):
        return (
            f"Drug interaction: {d.get('drug_a', '')} and {d.get('drug_b', '')}. "
            f"Risk: {d.get('risk', '')}. "
            f"{d.get('summary', '')} "
            f"Evidence: {d.get('evidence', '')} "
            f"Alternatives: {d.get('alternatives', '')}"
        )

    openai_client = openai_client or get_client()
    chroma_client = chroma_client or get_chroma_client()
    collection = chroma_client.get_or_create_collection(
        name=CHROMA_COLLECTION_NAME,
        metadata={"description": "PrescribeMe drug interaction evidence"},
    )

    texts = [_doc_to_text(d) for d in docs]
    ids = [f"sample_legacy_{i}" for i in range(len(docs))]
    embeddings = embed_texts(openai_client, texts)
    metadatas = [
        {
            "drug_a": str(d.get("drug_a", "")),
            "drug_b": str(d.get("drug_b", "")),
            "risk": str(d.get("risk", "")),
            "summary": str(d.get("summary", "")),
            "evidence": str(d.get("evidence", "")),
            "alternatives": str(d.get("alternatives", "")),
            "confidence": str(d.get("confidence", "")),
            "source": "sample",
        }
        for d in docs
    ]
    collection.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
    return len(docs)
