import sqlite3
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "mocka-governance-kernel" / "governance" / "governance.db"

def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest()

def main():
    conn = sqlite3.connect(str(DB))
    conn.row_factory = sqlite3.Row
    ledger="governance_ledger_event"

    last = conn.execute("SELECT * FROM governance_ledger_event ORDER BY rowid DESC LIMIT 1").fetchone()
    prev_event_id = last["event_id"]
    anchor_target_hash = last["chain_hash"]

    payload = {
        "anchor_target_chain_hash": anchor_target_hash,
        "issued_utc": datetime.now(timezone.utc).isoformat()
    }

    payload_json = json.dumps(payload, separators=(',',':'))
    event_id = sha256(prev_event_id + payload_json)
    timestamp = datetime.now(timezone.utc).isoformat()
    chain_material = prev_event_id + timestamp + "ANCHOR_PROOF" + payload_json
    chain_hash = sha256(chain_material)

    conn.execute(
        "INSERT INTO governance_ledger_event (event_id, prev_event_id, timestamp_utc, event_type, payload_json, note, chain_hash) VALUES (?,?,?,?,?,?,?)",
        (event_id, prev_event_id, timestamp, "ANCHOR_PROOF", payload_json, "Phase15 Anchor Proof Issued", chain_hash)
    )

    conn.commit()
    conn.close()

    print(json.dumps({"status":"ANCHOR_PROOF_ISSUED","event_id":event_id,"chain_hash":chain_hash},indent=2))

if __name__=="__main__":
    main()
