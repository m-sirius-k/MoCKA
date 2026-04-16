# NOTE: issue_governance_envelope_v2.py (Phase16 T11 full rewrite)
# NOTE: Purpose: issue Envelope v2 for a governance_ledger_event row (event_id-based).
# NOTE: Default public key path is used if env MOCKA_PHASE16_PUBKEY_PATH is missing.
# NOTE: Optional in-script signing if env MOCKA_PHASE16_PRIVKEY_PATH points to an Ed25519 private pem.
# NOTE: Canonical signed bytes MUST be deterministic (ASCII, LF only, trailing LF required).
# NOTE: Outputs are written to:
# NOTE:   C:\Users\sirok\MoCKA\outbox\

import os
import sys
import json
import base64
import hashlib
import sqlite3
from datetime import datetime, timezone

GOV_DB = r"C:\Users\sirok\MoCKA\mocka-governance-kernel\governance\governance.db"
GOV_TABLE = "governance_ledger_event"

OUTBOX = r"C:\Users\sirok\MoCKA\outbox"

PUBKEY_PATH_ENV = "MOCKA_PHASE16_PUBKEY_PATH"
PRIVKEY_PATH_ENV = "MOCKA_PHASE16_PRIVKEY_PATH"

DEFAULT_PUBKEY_PATH = r"C:\Users\sirok\MoCKA\secrets\phase16\ed25519_public.pem"

def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)

def read_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()

def sha256_hex_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def key_id_from_pubkey_pem(pubkey_pem_path: str) -> str:
    # key_id = sha256(pem bytes) hex with prefix for clarity
    pem = read_bytes(pubkey_pem_path)
    return "sha256:" + sha256_hex_bytes(pem)

def build_signed_bytes(scheme_version: str, event_id: str, chain_hash: str, timestamp_utc: str, payload_hash_sha256: str, key_id: str) -> bytes:
    # ASCII lines, LF only, trailing LF required
    text = (
        f"scheme_version={scheme_version}\n"
        f"event_id={event_id}\n"
        f"chain_hash={chain_hash}\n"
        f"timestamp_utc={timestamp_utc}\n"
        f"payload_hash_sha256={payload_hash_sha256}\n"
        f"key_id={key_id}\n"
    )
    return text.encode("ascii")

def try_sign_ed25519(privkey_pem_path: str, signed_bytes: bytes) -> str:
    # returns base64 signature, raises on failure
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    pem = read_bytes(privkey_pem_path)
    key = serialization.load_pem_private_key(pem, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError("Private key is not Ed25519")
    sig = key.sign(signed_bytes)  # 64 bytes
    return base64.b64encode(sig).decode("ascii")

def fetch_event(conn: sqlite3.Connection, event_id: str):
    cur = conn.cursor()
    cur.execute(
        f"SELECT event_id, prev_event_id, timestamp_utc, event_type, payload_json, note, chain_hash FROM {GOV_TABLE} WHERE event_id=?;",
        (event_id,),
    )
    row = cur.fetchone()
    if row is None:
        return None
    return {
        "event_id": row[0],
        "prev_event_id": row[1],
        "timestamp_utc": row[2],
        "event_type": row[3],
        "payload_json": row[4],
        "note": row[5],
        "chain_hash": row[6],
    }

def main():
    if len(sys.argv) != 2:
        print("Usage: python issue_governance_envelope_v2.py <event_id>")
        sys.exit(2)

    event_id = sys.argv[1].strip()

    ensure_dir(OUTBOX)

    pubkey_path = os.environ.get(PUBKEY_PATH_ENV, "").strip()
    if not pubkey_path:
        pubkey_path = DEFAULT_PUBKEY_PATH

    if not os.path.exists(pubkey_path):
        print("FAIL: public key pem not found at path:", pubkey_path)
        print("To override, set env and rerun:")
        print(f"  setx {PUBKEY_PATH_ENV} C:\\path\\to\\ed25519_public.pem")
        sys.exit(1)

    key_id = key_id_from_pubkey_pem(pubkey_path)

    if not os.path.exists(GOV_DB):
        print("FAIL: governance.db not found at path:", GOV_DB)
        sys.exit(1)

    conn = sqlite3.connect(GOV_DB)
    try:
        ev = fetch_event(conn, event_id)
        if ev is None:
            print("FAIL: event_id not found in governance.db:", event_id)
            sys.exit(1)

        # payload_hash_sha256: sha256 of payload_json bytes exactly as stored in DB (utf-8 encoding)
        payload_bytes = (ev["payload_json"] or "").encode("utf-8")
        payload_hash_sha256 = sha256_hex_bytes(payload_bytes)

        scheme_version = "v2"
        signed_bytes = build_signed_bytes(
            scheme_version=scheme_version,
            event_id=ev["event_id"],
            chain_hash=ev["chain_hash"],
            timestamp_utc=ev["timestamp_utc"],
            payload_hash_sha256=payload_hash_sha256,
            key_id=key_id,
        )

        prefix = f"governance_envelope_v2_{ev['event_id']}"
        payload_out = os.path.join(OUTBOX, f"{prefix}.payload_json.txt")
        signed_bytes_out = os.path.join(OUTBOX, f"{prefix}.signed_bytes.txt")
        envelope_out = os.path.join(OUTBOX, f"{prefix}.json")

        with open(payload_out, "wb") as f:
            f.write(payload_bytes)

        with open(signed_bytes_out, "wb") as f:
            f.write(signed_bytes)

        envelope = {
            "scheme_version": "v2",
            "event_id": ev["event_id"],
            "chain_hash": ev["chain_hash"],
            "timestamp_utc": ev["timestamp_utc"],
            "payload_hash_sha256": payload_hash_sha256,
            "key_id": key_id,
            "signature_format": "base64",
            "signature_ed25519": "",
            "notes": f"issued_utc={utc_now()} event_type={ev['event_type']}"
        }

        privkey_path = os.environ.get(PRIVKEY_PATH_ENV, "").strip()
        if privkey_path and os.path.exists(privkey_path):
            try:
                sig_b64 = try_sign_ed25519(privkey_path, signed_bytes)
                envelope["signature_ed25519"] = sig_b64
                envelope["notes"] += " signed_in_script=true"
            except Exception as e:
                envelope["notes"] += f" signed_in_script=false sign_error={str(e)}"
        else:
            envelope["notes"] += " signed_in_script=false reason=missing_privkey_env"

        with open(envelope_out, "w", encoding="utf-8") as f:
            json.dump(envelope, f, indent=2)

        print("OK: wrote envelope:", envelope_out)
        print("OK: wrote payload bytes:", payload_out)
        print("OK: wrote signed bytes:", signed_bytes_out)
        if envelope["signature_ed25519"]:
            print("OK: signature_ed25519 embedded (base64)")
        else:
            print("NOTE: signature_ed25519 is empty.")
            print("To sign in-script, set env and rerun:")
            print(f"  setx {PRIVKEY_PATH_ENV} C:\\path\\to\\ed25519_private.pem")

    finally:
        conn.close()

if __name__ == "__main__":
    main()