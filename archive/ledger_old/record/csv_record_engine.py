import csv
import os
import uuid
from datetime import datetime

ACTIVE_PATH = "runtime/record/active_log.csv"
ARCHIVE_PATH = "runtime/record/archive_log.csv"

FIELDS = ["timestamp","event_id","type","summary","storage_path","count"]

ALLOWED_TYPES = ["incident","instruction","chat","system","audit"]

def normalize_type(t):
    if t not in ALLOWED_TYPES:
        return "system"
    return t

def init_csv(path):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path,"w",newline="",encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f,fieldnames=FIELDS)
            writer.writeheader()

def load_last_row():
    if not os.path.exists(ACTIVE_PATH):
        return None

    with open(ACTIVE_PATH,"r",encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
        if not rows:
            return None
        return rows[-1]

def record_event(event_type, summary, storage_path=""):
    init_csv(ACTIVE_PATH)

    event_type = normalize_type(event_type)

    last = load_last_row()

    # --- ノイズ圧縮 ---
    if last and last["summary"] == summary and last["type"] == event_type:
        rows = []
        with open(ACTIVE_PATH,"r",encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))

        rows[-1]["count"] = str(int(rows[-1].get("count","1")) + 1)

        with open(ACTIVE_PATH,"w",newline="",encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f,fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)

        return rows[-1]

    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_id": str(uuid.uuid4()),
        "type": event_type,
        "summary": summary,
        "storage_path": storage_path,
        "count": "1"
    }

    with open(ACTIVE_PATH,"a",newline="",encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f,fieldnames=FIELDS)
        writer.writerow(event)

    return event

def archive_if_needed(limit=100):
    init_csv(ACTIVE_PATH)
    init_csv(ARCHIVE_PATH)

    with open(ACTIVE_PATH,"r",encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    if len(rows) <= limit:
        return

    move = rows[:-limit]
    keep = rows[-limit:]

    with open(ARCHIVE_PATH,"a",newline="",encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f,fieldnames=FIELDS)
        writer.writerows(move)

    with open(ACTIVE_PATH,"w",newline="",encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f,fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(keep)
