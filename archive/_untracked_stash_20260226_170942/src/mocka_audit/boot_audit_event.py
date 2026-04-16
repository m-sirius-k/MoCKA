# FILE: C:\Users\sirok\MoCKA\src\mocka_audit\boot_audit_event.py
import sqlite3
from pathlib import Path
from datetime import datetime
import json
import hashlib

DB_PATH = Path(r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db")

def write_boot_event(entry_path: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    created_at = datetime.utcnow().isoformat()

    payload = {
        "type": "boot_event",
        "entry_path": entry_path,
        "created_at": created_at
    }

    event_content = json.dumps(payload, separators=(",", ":"))

    event_id = hashlib.sha256(event_content.encode()).hexdigest()

    cur.execute(
        "INSERT INTO audit_ledger_event "
        "(event_id, chain_hash, prev_event_id, event_content, contract_version, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            event_id,
            event_id,
            None,
            event_content,
            "mocka.audit.v1",
            created_at
        )
    )

    conn.commit()
    conn.close()

    print(f"BOOT_EVENT_WRITTEN: {event_id}")

if __name__ == "__main__":
    write_boot_event("manual_boot")
