import os
import sys
import json
import hashlib
import sqlite3
from pathlib import Path
from datetime import datetime, UTC

ROOT = Path(r"C:\Users\sirok\MoCKA\audit")
DB_PATH = ROOT / "ed25519" / "audit.db"
LAST_EVENT_FILE = ROOT / "last_event_id.txt"

def sha256_hex(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def load_last_event_id():
    if LAST_EVENT_FILE.exists():
        return LAST_EVENT_FILE.read_text(encoding="utf-8").strip()
    return None

def save_last_event_id(event_id: str):
    LAST_EVENT_FILE.write_text(event_id, encoding="utf-8")

def append_event(note_text: str):
    now_utc = datetime.now(UTC).isoformat()

    event_content = {
        "note": note_text,
        "utc": now_utc
    }

    content_json = json.dumps(
        event_content,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":")
    )
    content_bytes = content_json.encode("utf-8")

    event_id = sha256_hex(content_bytes)
    previous_event_id = load_last_event_id()

    if previous_event_id:
        chain_hash = sha256_hex((previous_event_id + event_id).encode("utf-8"))
    else:
        chain_hash = event_id

    event_filename = ROOT / f"{event_id}.json"
    event_data = {
        "event_id": event_id,
        "previous_event_id": previous_event_id,
        "chain_hash": chain_hash,
        "event_content": event_content   # ← ここを統一
    }

    with open(event_filename, "w", encoding="utf-8") as f:
        json.dump(event_data, f, ensure_ascii=False, indent=2)
        f.flush()
        os.fsync(f.fileno())

    save_last_event_id(event_id)

    conn = sqlite3.connect(str(DB_PATH))
    try:
        cur = conn.cursor()
        cur.execute("BEGIN")
        cur.execute(
            """
            INSERT INTO audit_ledger_event
            (event_id, previous_event_id, chain_hash, event_content, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (event_id, previous_event_id, chain_hash, content_json, now_utc)
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    return event_id

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python audit\\atomic_append.py \"note text\"")
        sys.exit(1)

    note_text = sys.argv[1]
    eid = append_event(note_text)
    print("EVENT:", eid)