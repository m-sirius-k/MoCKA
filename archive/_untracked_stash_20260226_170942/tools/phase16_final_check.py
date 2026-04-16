import sqlite3
import json
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

ROOT = Path(r"C:\Users\sirok\MoCKA")

GOV_DB = ROOT / r"mocka-governance-kernel\governance\governance.db"
AUD_DB = ROOT / r"audit\ed25519\audit.db"
INTEG_DB = ROOT / r"infield\phase16\db\integrity.db"

def main():
    govtip = (ROOT / r"governance\last_governance_event_id.txt").read_text(encoding="utf-8").strip()
    audit_tip = (ROOT / r"audit\last_event_id.txt").read_text(encoding="utf-8").strip()

    cg = sqlite3.connect(str(GOV_DB))
    cg.row_factory = sqlite3.Row
    ok_g = cg.execute(
        "SELECT 1 FROM governance_ledger_event WHERE event_id=?",
        (govtip,)
    ).fetchone() is not None

    anchor = cg.execute(
        "SELECT event_id FROM governance_ledger_event "
        "WHERE event_type='ANCHOR_PROOF' "
        "ORDER BY rowid DESC LIMIT 1"
    ).fetchone()
    cg.close()

    ca = sqlite3.connect(str(AUD_DB))
    ok_a = ca.execute(
        "SELECT 1 FROM audit_ledger_event WHERE event_id=?",
        (audit_tip,)
    ).fetchone() is not None
    ca.close()

    payload = (ROOT / r"outbox\governance_anchor_proof_payload.json").read_bytes()
    sig = (ROOT / r"secrets\phase16\governance_anchor_proof_payload.sig").read_bytes()
    pub = (ROOT / r"secrets\phase16\ed25519_public.pem").read_bytes()

    pk = Ed25519PublicKey.from_public_bytes(pub) if len(pub) == 32 else serialization.load_pem_public_key(pub)
    pk.verify(sig, payload)
    sig_ok = True

    ci = sqlite3.connect(str(INTEG_DB))
    ci.row_factory = sqlite3.Row
    rec = ci.execute(
        "SELECT id FROM reconciliation_log "
        "WHERE event_type='ANCHOR_PROOF' "
        "ORDER BY id DESC LIMIT 1"
    ).fetchone()

    att = ci.execute(
        "SELECT attestation_id FROM attestation_log "
        "WHERE anchor_id=? "
        "ORDER BY rowid DESC LIMIT 1",
        (anchor["event_id"],)
    ).fetchone()
    ci.close()

    result = {
        "gov_tip_ok": ok_g,
        "audit_tip_ok": ok_a,
        "sig_ok": sig_ok,
        "reconciliation_ok": rec is not None,
        "attestation_ok": att is not None and att["attestation_id"] is not None
    }

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
