import sqlite3
import json
import hashlib
from pathlib import Path

ROOT = Path(r"C:\Users\sirok\MoCKA")
GOV_DB = ROOT / r"mocka-governance-kernel\governance\governance.db"
INTEG_DB = ROOT / r"infield\phase16\db\integrity.db"
PAYLOAD = ROOT / r"outbox\governance_anchor_proof_payload.json"
SIG = ROOT / r"secrets\phase16\governance_anchor_proof_payload.sig"
PUB = ROOT / r"secrets\phase16\ed25519_public.pem"
OUT = ROOT / r"outbox\phase16_fixed_artifacts.json"

def sha256_file(p: Path):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    cg = sqlite3.connect(str(GOV_DB))
    cg.row_factory = sqlite3.Row
    gov = cg.execute(
        "SELECT event_id,chain_hash,timestamp_utc FROM governance_ledger_event "
        "WHERE event_type='ANCHOR_PROOF' ORDER BY rowid DESC LIMIT 1"
    ).fetchone()
    cg.close()

    ci = sqlite3.connect(str(INTEG_DB))
    ci.row_factory = sqlite3.Row
    rec = ci.execute(
        "SELECT * FROM reconciliation_log WHERE event_type='ANCHOR_PROOF' ORDER BY id DESC LIMIT 1"
    ).fetchone()
    att = ci.execute(
        "SELECT rowid,* FROM attestation_log WHERE anchor_id=? ORDER BY rowid DESC LIMIT 1",
        (gov["event_id"],)
    ).fetchone()
    ci.close()

    manifest = {
        "phase": "16",
        "governance": dict(gov),
        "reconciliation": dict(rec) if rec else None,
        "attestation": dict(att) if att else None,
        "artifacts": {
            "payload_sha256": sha256_file(PAYLOAD),
            "sig_sha256": sha256_file(SIG),
            "pubkey_sha256": sha256_file(PUB),
            "sig_len": len(SIG.read_bytes())
        }
    }

    OUT.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print("MANIFEST_REGENERATED")

if __name__ == "__main__":
    main()
