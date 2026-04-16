import json
import sqlite3
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import ed25519

BASE = Path(r"C:\Users\sirok\MoCKA")
DB_PATH = BASE / r"audit\ed25519\audit.db"
PRIVATE_KEY_PATH = BASE / r"secrets\ed25519\ed25519_private.key"

# 正しい message_canonical（1行・空白なし）
message_canonical = '{"date":"2026-02-20","file_chain_length":6,"final_chain_hash":"08afc59c8e975fbcad69af161c2057eab41f48a0444b0bc6aa4acf97e0895813","ledger_count":2}'

raw_priv = PRIVATE_KEY_PATH.read_bytes()
priv = ed25519.Ed25519PrivateKey.from_private_bytes(raw_priv)

signature = priv.sign(message_canonical.encode("utf-8")).hex()

payload = {
    "message_canonical": message_canonical,
    "signature_hex": signature
}

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute("""
INSERT INTO audit_ledger_event
(event_type, schema_version, event_content, event_id, prev_chain_hash, chain_hash, created_at_utc)
VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
""", (
    "daily_signature",
    "1",
    json.dumps(payload, separators=(",", ":")),
    "resigned_daily_signature",
    None,
    "PENDING_CHAIN_HASH"
))

conn.commit()
conn.close()

print("NEW SIGNATURE:", signature[:32])