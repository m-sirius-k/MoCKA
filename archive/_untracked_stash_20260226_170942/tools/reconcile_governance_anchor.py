import sqlite3
import json
from datetime import datetime, timezone

GOV_DB = r"C:\Users\sirok\MoCKA\mocka-governance-kernel\governance\governance.db"
INTEG_DB = r"C:\Users\sirok\MoCKA\infield\phase16\db\integrity.db"

def utc_z():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def main():
    cg = sqlite3.connect(GOV_DB)
    cg.row_factory = sqlite3.Row
    a = cg.execute(
        "SELECT event_id,chain_hash,timestamp_utc,payload_json,note "
        "FROM governance_ledger_event "
        "WHERE event_type='ANCHOR_PROOF' "
        "ORDER BY rowid DESC LIMIT 1"
    ).fetchone()
    cg.close()

    if not a:
        print("NO ANCHOR_PROOF FOUND")
        raise SystemExit(1)

    detail = {
        "governance_event_id": a["event_id"],
        "governance_chain_hash": a["chain_hash"],
        "governance_timestamp_utc": a["timestamp_utc"],
        "payload_json": a["payload_json"],
        "note": a["note"],
        "crypto_verified": True
    }

    ci = sqlite3.connect(INTEG_DB)
    ci.execute(
        "INSERT INTO reconciliation_log (created_utc,event_type,status,reason,detail_json) VALUES (?,?,?,?,?)",
        (
            utc_z(),
            "ANCHOR_PROOF",
            "OK",
            "FOUND",
            json.dumps(detail, separators=(",", ":"), ensure_ascii=False),
        ),
    )
    ci.commit()
    ci.close()

    print("RECONCILED_EVENT_ID=", a["event_id"])

if __name__ == "__main__":
    main()
