"""OpenAI embeddings for interaction documents and queries."""
from openai import OpenAI

from config import EMBEDDING_MODEL, OPENAI_API_KEY


def get_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY is not set. Add it to .env or environment.")
    return OpenAI(api_key=OPENAI_API_KEY)


def embed_texts(client: OpenAI, texts: list[str], model: str = EMBEDDING_MODEL) -> list[list[float]]:
    """Embed a list of texts. Handles batching for API limits."""
    if not texts:
        return []
    response = client.embeddings.create(input=texts, model=model)
    return [item.embedding for item in sorted(response.data, key=lambda x: x.index)]


def embed_single(client: OpenAI, text: str, model: str = EMBEDDING_MODEL) -> list[float]:
    """Embed a single string."""
    result = embed_texts(client, [text], model=model)
    return result[0] if result else []
