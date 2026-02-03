"""
Convert a DrugBank interaction export (CSV) into data/drugbank_interactions.json
for the PrescribeMe KB. Run from project root: python -m scripts.ingest_drugbank <path_to_csv>
Adjust column mapping below if your DrugBank export uses different headers.
"""
import csv
import json
import sys
from pathlib import Path

# Project root = parent of scripts/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUT_PATH = DATA_DIR / "drugbank_interactions.json"


# Map your CSV columns to PrescribeMe schema. Adjust keys to match your export.
COLUMN_MAP = {
    "drug_a": "drug1",           # or "Drug 1", "object_drug", etc.
    "drug_b": "drug2",           # or "Drug 2", "precipitant_drug", etc.
    "risk": "severity",          # or "Risk", "level"; normalize to low/moderate/high
    "summary": "description",    # or "Summary", "interaction_summary"
    "evidence": "evidence",      # or "Evidence", "mechanism"; leave "" if missing
    "alternatives": "alternatives",  # optional
    "confidence": "confidence",  # optional
}


def normalize_risk(value: str) -> str:
    v = (value or "").strip().lower()
    if v in ("high", "major", "severe", "contraindicated"):
        return "high"
    if v in ("moderate", "moderate", "medium"):
        return "moderate"
    if v in ("low", "minor"):
        return "low"
    return v or "moderate"


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.ingest_drugbank <path_to_drugbank_export.csv>")
        sys.exit(1)
    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"File not found: {csv_path}")
        sys.exit(1)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    with open(csv_path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
        headers = [h.strip() for h in (reader.fieldnames or [])]
        # If your CSV uses different column names, update COLUMN_MAP or detect here
        for row in reader:
            doc = {}
            for our_key, their_key in COLUMN_MAP.items():
                val = row.get(their_key) or row.get(our_key) or ""
                if isinstance(val, str):
                    val = val.strip()
                if our_key == "risk":
                    val = normalize_risk(str(val))
                doc[our_key] = val
            if doc.get("drug_a") or doc.get("drug_b") or doc.get("summary"):
                rows.append(doc)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(rows)} interactions to {OUT_PATH}")
    print("Next: run 'Initialize knowledge base' in the app or: python -m scripts.build_kb")


if __name__ == "__main__":
    main()
