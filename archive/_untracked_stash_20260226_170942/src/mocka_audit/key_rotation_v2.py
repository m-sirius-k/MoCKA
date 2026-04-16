import sqlite3
from datetime import datetime, UTC

from audit_writer import AuditWriter

DB_PATH = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"


def rotate_key(old_key: str, new_key: str) -> None:
    now = datetime.now(UTC).isoformat()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "UPDATE key_metadata SET status='revoked', valid_to=? WHERE key_id=?",
        (now, old_key)
    )

    cur.execute(
        "INSERT OR REPLACE INTO key_metadata (key_id, status, valid_from) VALUES (?, 'active', ?)",
        (new_key, now)
    )

    conn.commit()
    conn.close()

    writer = AuditWriter(DB_PATH)
    ev = writer.write_payload({
        "type": "key_rotation",
        "old_key": old_key,
        "new_key": new_key,
        "rotated_at": now,
    }, note="key_rotation_v2", commit=True)

    print("KEY_ROTATED_CONNECTED:", ev["event_id"])


if __name__ == "__main__":
    rotate_key("test-key-001", "test-key-002")