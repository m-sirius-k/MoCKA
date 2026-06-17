import json
from pathlib import Path

FILE = Path(__file__).parent.parent.parent / "data" / "evaluation_history.jsonl"


def get_caliber_snapshot():
    if not FILE.exists():
        return {"score": 0, "items": []}

    with open(FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    items = [json.loads(l) for l in lines[-20:] if l.strip()]

    if not items:
        return {"score": 0, "items": []}

    avg = sum(i.get("score", 0) for i in items) / len(items)

    return {
        "score": round(avg, 3),
        "items": items
    }
