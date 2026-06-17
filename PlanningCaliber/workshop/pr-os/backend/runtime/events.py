import json
import time
from pathlib import Path

EVENT_FILE = Path(__file__).parent.parent.parent / "data" / "events.jsonl"


def append_event(action: str, result: dict):
    event = {
        "ts": time.time(),
        "action": action,
        "result": result
    }
    EVENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def read_events(limit: int = 50):
    if not EVENT_FILE.exists():
        return []

    with open(EVENT_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    return [json.loads(l) for l in lines[-limit:]]
