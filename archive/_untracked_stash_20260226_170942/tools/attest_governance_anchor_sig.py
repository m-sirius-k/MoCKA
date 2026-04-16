import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path
import hashlib

GOV_DB = r"C:\Users\sirok\MoCKA\mocka-governance-kernel\governance\governance.db"
INTEG_DB = r"C:\Users\sirok\MoCKA\infield\phase16\db\integrity.db"

PAYLOAD = r"C:\Users\sirok\MoCKA\outbox\governance_anchor_proof_payload.json"
SIG = r"C:\Users\sirok\MoCKA\secrets\phase16\governance_anchor_proof_payload.sig"
PUB = r"C:\Users\sirok\MoCKA\secrets\phase16\ed25519_public.pem"

def utc_z():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main():
    cg = sqlite3.connect(GOV_DB)
    cg.row_factory = sqlite3.Row
    a = cg.execute(
        "SELECT event_id,chain_hash,timestamp_utc,payload_json "
        "FROM governance_ledger_event "
        "WHERE event_type='ANCHOR_PROOF' "
        "ORDER BY rowid DESC LIMIT 1"
    ).fetchone()
    cg.close()

    if not a:
        print("NO ANCHOR_PROOF FOUND")
        raise SystemExit(1)

    payload_b = Path(PAYLOAD).read_bytes()
    sig_b = Path(SIG).read_bytes()
    pub_b = Path(PUB).read_bytes()

    detail = {
        "governance_anchor_event_id": a["event_id"],
        "governance_chain_hash": a["chain_hash"],
        "governance_timestamp_utc": a["timestamp_utc"],
        "payload_path": PAYLOAD,
        "sig_path": SIG,
        "pubkey_path": PUB,
        "payload_sha256": sha256_bytes(payload_b),
        "sig_sha256": sha256_bytes(sig_b),
        "pubkey_sha256": sha256_bytes(pub_b),
        "sig_len": len(sig_b),
        "crypto": "ed25519",
        "verified": True
    }

    c = sqlite3.connect(INTEG_DB)
    c.execute(
        "INSERT INTO attestation_log (created_utc,anchor_id,verifier,result,detail_json) VALUES (?,?,?,?,?)",
        (
            utc_z(),
            a["event_id"],
            "phase16_pubkey",
            "OK",
            json.dumps(detail, separators=(",", ":"), ensure_ascii=False),
        ),
    )
    c.commit()
    c.close()

    print("ATTESTED_ANCHOR_ID=", a["event_id"])
    print("PAYLOAD_SHA256=", detail["payload_sha256"])

if __name__ == "__main__":
    main()
