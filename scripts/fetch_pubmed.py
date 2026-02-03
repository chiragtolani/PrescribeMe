"""
Fetch PubMed abstracts and save to data/pubmed_abstracts.json.
Run from project root: python -m scripts.fetch_pubmed [query] [max_results]
Example: python -m scripts.fetch_pubmed "drug interaction warfarin" 50
Uses NCBI E-utilities (no API key required). Rate limit: 3 requests/sec without key.
"""
import json
import sys
import time
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUT_PATH = DATA_DIR / "pubmed_abstracts.json"
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def fetch_ids(query: str, max_results: int = 50) -> list[str]:
    """E-search: get PMIDs for a query."""
    params = {"db": "pubmed", "term": query, "retmax": max_results, "retmode": "json"}
    url = f"{BASE}/esearch.fcgi?{urlencode(params)}"
    with urlopen(url, timeout=15) as r:
        data = json.load(r)
    ids = data.get("esearchresult", {}).get("idlist", [])
    return ids


def fetch_abstracts(pmids: list[str]) -> list[dict]:
    """E-fetch: get title + abstract for each PMID."""
    if not pmids:
        return []
    params = {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"}
    url = f"{BASE}/efetch.fcgi?{urlencode(params)}"
    with urlopen(url, timeout=30) as r:
        xml = r.read().decode("utf-8", errors="replace")

    # Minimal XML parse for <ArticleTitle> and <AbstractText>
    import re
    articles = re.findall(r"<PubmedArticle>.*?</PubmedArticle>", xml, re.DOTALL)
    out = []
    for art in articles:
        pmid = re.search(r"<PMID[^>]*>(\d+)</PMID>", art)
        title = re.search(r"<ArticleTitle>([^<]*)</ArticleTitle>", art)
        abstract_parts = re.findall(r"<AbstractText[^>]*>([^<]*)</AbstractText>", art)
        abstract = " ".join(abstract_parts).strip() if abstract_parts else ""
        if not pmid:
            continue
        out.append({
            "pmid": pmid.group(1),
            "title": (title.group(1) if title else "").strip(),
            "abstract": abstract,
        })
    return out


def main():
    query = "drug drug interaction clinical"
    max_results = 30
    if len(sys.argv) >= 2:
        query = sys.argv[1]
    if len(sys.argv) >= 3:
        max_results = min(int(sys.argv[2]), 100)

    print(f"Searching PubMed: {query!r} (max {max_results})")
    ids = fetch_ids(query, max_results)
    print(f"Found {len(ids)} PMIDs")
    if not ids:
        print("No results. Writing empty list.")
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(OUT_PATH, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)
        return

    time.sleep(0.4)  # rate limit
    abstracts = fetch_abstracts(ids)
    print(f"Fetched {len(abstracts)} abstracts")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(abstracts, f, indent=2, ensure_ascii=False)
    print(f"Wrote {OUT_PATH}")
    print("Next: run 'Initialize knowledge base' in the app or: python -m scripts.build_kb")


if __name__ == "__main__":
    main()
