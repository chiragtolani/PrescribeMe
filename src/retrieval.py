"""Retrieve relevant interaction evidence from Chroma."""
from config import CHROMA_COLLECTION_NAME, MIN_RELEVANCE_SCORE, TOP_K_RETRIEVAL
from src.chroma_store import get_chroma_client
from src.embeddings import embed_single, get_client


def retrieve_for_prescription(
    prescription_text: str,
    patient_context: str = "",
    top_k: int = TOP_K_RETRIEVAL,
    min_score: float = MIN_RELEVANCE_SCORE,
):
    """Retrieve top-k interaction documents relevant to prescription + patient context."""
    query = prescription_text
    if patient_context:
        query = f"Prescription: {prescription_text}. Patient context: {patient_context}."

    openai_client = get_client()
    chroma_client = get_chroma_client()
    collection = chroma_client.get_collection(name=CHROMA_COLLECTION_NAME)
    query_embedding = embed_single(openai_client, query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    if not results or not results["ids"] or not results["ids"][0]:
        return []

    # Chroma returns distances (lower = more similar). Convert to simple relevance.
    out = []
    for i, doc_id in enumerate(results["ids"][0]):
        dist = results["distances"][0][i] if results["distances"] else 0
        # Simple relevance: 1 / (1 + distance). Tune min_score as needed.
        score = 1.0 / (1.0 + dist)
        if score < min_score:
            continue
        meta = (results["metadatas"][0][i]) if results["metadatas"] else {}
        doc_text = (results["documents"][0][i]) if results["documents"] else ""
        out.append(
            {
                "id": doc_id,
                "score": round(score, 4),
                "document": doc_text,
                "metadata": meta,
            }
        )
    return out
