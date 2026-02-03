"""
Build the RAG knowledge base on Chroma from data/sample_interactions.json,
data/drugbank_interactions.json, and data/pubmed_abstracts.json.
Run from project root: python -m scripts.build_kb
"""
from src.chroma_store import build_knowledge_base


def main():
    count = build_knowledge_base(clear_first=True)
    print(f"Knowledge base ready: {count} documents indexed.")


if __name__ == "__main__":
    main()
