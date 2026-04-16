"""
infield_ingestor.py
runtime/storage/infield/*.txt を読み込み
最新1件をruntime/input.jsonに変換してmain_loopに渡す
"""
import os
import json
import uuid
from datetime import datetime, timezone

INFIELD_DIR = r"C:\Users\sirok\MoCKA\runtime\storage\infield"
INPUT_PATH  = r"C:\Users\sirok\MoCKA\runtime\input.json"
DONE_LOG    = r"C:\Users\sirok\MoCKA\runtime\storage\infield\processed.json"

def load_done():
    if os.path.exists(DONE_LOG):
        with open(DONE_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_done(done):
    with open(DONE_LOG, "w", encoding="utf-8") as f:
        json.dump(done, f, indent=2)

def ingest():
    done = load_done()
    files = sorted([
        f for f in os.listdir(INFIELD_DIR)
        if f.endswith(".txt") and f not in done
    ])

    if not files:
        print("NO NEW INFIELD FILES")
        return False

    target = files[0]
    path = os.path.join(INFIELD_DIR, target)
    text = open(path, "r", encoding="utf-8").read().strip()

    intent = {
        "intent": {
            "intent_id":  str(uuid.uuid4()),
            "session_id": "infield_session",
            "type":       "command",
            "goal":       text,
            "action":     text,
            "context":    text,
            "constraints": "",
            "source":     "infield",
            "timestamp":  datetime.now(timezone.utc).isoformat(),
            "confidence": 0.8,
            "priority":   1
        }
    }

    with open(INPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(intent, f, ensure_ascii=False, indent=2)

    done.append(target)
    save_done(done)

    print(f"INGEST: {target} → input.json")
    print(f"GOAL: {text[:80]}")
    return True

if __name__ == "__main__":
    ingest()
