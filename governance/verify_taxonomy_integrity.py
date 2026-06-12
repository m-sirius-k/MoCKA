from __future__ import annotations
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TAXONOMY_PATH = ROOT / "docs" / "mocka3" / "taxonomy.json"


def main() -> int:
    if not TAXONOMY_PATH.exists():
        print("FAIL: taxonomy.json not found")
        return 2

    taxonomy = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))

    if taxonomy.get("status") != "FROZEN":
        print("FAIL: taxonomy.json is not FROZEN")
        return 3

    if taxonomy.get("version") != "1.1":
        print(f"FAIL: Expected v1.1, got {taxonomy.get('version')}")
        return 4

    categories = taxonomy.get("categories", {})
    if len(categories) != 7:
        print(f"FAIL: Expected 7 categories, got {len(categories)}")
        return 5

    events = taxonomy.get("events", {})
    total_events = sum(len(cat_events) for cat_events in events.values())
    if total_events < 37:
        print(f"FAIL: Expected 37+ events, got {total_events}")
        return 6

    print("OK: taxonomy_integrity")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
