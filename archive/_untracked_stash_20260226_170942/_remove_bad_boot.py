# FILE: C:\Users\sirok\MoCKA\_remove_bad_boot.py
import sqlite3
from pathlib import Path

BAD_EVENT_ID = "0fb490b82034a4cbf2063ed4ad9725b6cb1619672fe04d6d86dfc3c3836281d4"

db = Path(r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db")
conn = sqlite3.connect(db)
cur = conn.cursor()

cur.execute(
    "DELETE FROM audit_ledger_event WHERE event_id=?",
    (BAD_EVENT_ID,)
)

conn.commit()
conn.close()

print("BAD_BOOT_EVENT_REMOVED")
