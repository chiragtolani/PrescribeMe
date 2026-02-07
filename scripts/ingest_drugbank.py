"""
Convert a DrugBank interaction export (CSV or XML) into data/drugbank_interactions.json
for the PrescribeMe KB.

  CSV:  python -m scripts.ingest_drugbank <path_to_export.csv>
  XML:  python -m scripts.ingest_drugbank <path_to_full_database.xml>

XML format: DrugBank full database XML. Each <drug> has <name> and <drug-interactions>
with <drug-interaction> elements containing <name> and <description>. Uses iterative
parsing so large files (e.g. 17M+ lines) do not exhaust memory.
"""
import csv
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Project root = parent of scripts/
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUT_PATH = DATA_DIR / "drugbank_interactions.json"

# DrugBank XML namespace (default in full database export)
NS = "{http://www.drugbank.ca}"
DRUG = NS + "drug"
NAME = NS + "name"
DRUG_INTERACTIONS = NS + "drug-interactions"
DRUG_INTERACTION = NS + "drug-interaction"
DESCRIPTION = NS + "description"
DRUGBANK_ID = NS + "drugbank-id"

# Map your CSV columns to PrescribeMe schema. Adjust keys to match your export.
COLUMN_MAP = {
    "drug_a": "drug1",
    "drug_b": "drug2",
    "risk": "severity",
    "summary": "description",
    "evidence": "evidence",
    "alternatives": "alternatives",
    "confidence": "confidence",
}


def normalize_risk(value: str) -> str:
    v = (value or "").strip().lower()
    if v in ("high", "major", "severe", "contraindicated"):
        return "high"
    if v in ("moderate", "medium"):
        return "moderate"
    if v in ("low", "minor"):
        return "low"
    return v or "moderate"


def _infer_risk_from_description(description: str) -> str:
    """Infer risk level from interaction description text (DrugBank XML often has no severity)."""
    if not description:
        return "moderate"
    d = description.lower()
    if any(
        x in d
        for x in (
            "bleeding",
            "hemorrhage",
            "contraindicated",
            "major",
            "severe",
            "fatal",
            "death",
            "toxicity",
        )
    ):
        return "high"
    if any(x in d for x in ("minor", "observe", "monitor")):
        return "low"
    return "moderate"


def _text(elem: ET.Element | None) -> str:
    if elem is None:
        return ""
    return (elem.text or "").strip() or ""


def ingest_xml(xml_path: Path) -> list[dict]:
    """Parse DrugBank XML and return list of PrescribeMe-style interaction dicts.
    Uses iterparse to avoid loading the entire file into memory.
    """
    seen: set[tuple[str, str]] = set()  # (drug_a, drug_b) normalized to avoid duplicates
    rows: list[dict] = []
    count_drugs = 0
    count_skipped_empty = 0

    for _event, elem in ET.iterparse(xml_path, events=("end",)):
        if elem.tag != DRUG:
            continue
        # At </drug>: first direct <name> is this drug's name
        name_elem = elem.find(NAME)
        drug_name = _text(name_elem) if name_elem is not None else ""
        if not drug_name:
            elem.clear()
            continue

        interactions_elem = elem.find(DRUG_INTERACTIONS)
        if interactions_elem is None:
            elem.clear()
            continue

        for di in interactions_elem.findall(DRUG_INTERACTION):
            other_elem = di.find(NAME)
            desc_elem = di.find(DESCRIPTION)
            other_name = _text(other_elem) if other_elem is not None else ""
            desc = _text(desc_elem) if desc_elem is not None else ""
            if not other_name:
                count_skipped_empty += 1
                continue
            # Normalize pair so we don't store (A,B) and (B,A) as duplicates
            pair = tuple(sorted([drug_name, other_name]))
            if pair in seen:
                continue
            seen.add(pair)
            rows.append({
                "drug_a": drug_name,
                "drug_b": other_name,
                "risk": _infer_risk_from_description(desc),
                "summary": desc or f"Interaction between {drug_name} and {other_name}.",
                "evidence": "",
                "alternatives": "",
                "confidence": "high" if desc else "moderate",
            })

        count_drugs += 1
        if count_drugs % 500 == 0:
            print(f"  Processed {count_drugs} drugs, {len(rows)} interactions so far...")
        elem.clear()

    if count_skipped_empty:
        print(f"  Skipped {count_skipped_empty} interactions with missing drug name.")
    return rows


def ingest_csv(csv_path: Path) -> list[dict]:
    """Parse DrugBank CSV and return list of PrescribeMe-style interaction dicts."""
    rows = []
    with open(csv_path, newline="", encoding="utf-8", errors="replace") as f:
        reader = csv.DictReader(f)
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
    return rows


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m scripts.ingest_drugbank <path_to_export.csv|.xml>")
        sys.exit(1)
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}")
        sys.exit(1)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    suffix = path.suffix.lower()
    if suffix == ".xml":
        print(f"Parsing DrugBank XML: {path}")
        rows = ingest_xml(path)
    elif suffix in (".csv", ".txt"):
        print(f"Parsing CSV: {path}")
        rows = ingest_csv(path)
    else:
        print("Unsupported format. Use a .xml (DrugBank full) or .csv file.")
        sys.exit(1)

    if not rows:
        print("No interactions found. Check file format and content.")
        sys.exit(1)

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)

    print(f"Wrote {len(rows)} interactions to {OUT_PATH}")
    print("Next: run 'Initialize knowledge base' in the app or: python -m scripts.build_kb")


if __name__ == "__main__":
    main()
