# C:\Users\sirok\MoCKA\src\mocka_audit\verify_ledger_db.py
# NOTE: Phase9-B ledger(DB)専用検証。DBに格納された event_content 文字列をそのまま用いて chain_hash を検証する。
# NOTE: daily_signature は message_canonical を Ed25519 で検証。

import argparse
import hashlib
import json
import sqlite3
from typing import Any, Optional, Tuple, List

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

DEFAULT_DB = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"
DEFAULT_PUBKEY_HEX = "c2d0e53731df8bb527c571a5d1cd1d56a9270a6eff6002e00fd0a517cbf4642b"

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def as_text(raw: Any) -> str:
    if isinstance(raw, str):
        return raw
    return json.dumps(raw, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--pubkey-hex", default=DEFAULT_PUBKEY_HEX)
    args = ap.parse_args()

    pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(args.pubkey_hex))

    con = sqlite3.connect(args.db)
    try:
        cur = con.cursor()
        cur.execute("SELECT id,event_type,prev_chain_hash,chain_hash,event_content FROM audit_ledger_event ORDER BY id ASC")
        rows: List[Tuple[int, str, Optional[str], str, Any]] = cur.fetchall()

        prev: Optional[str] = None
        for (i, typ, prevh, chainh, content_raw) in rows:
            if prevh != prev:
                print("status: FAIL")
                print(f"reason: prev_link_mismatch id={i} expected={prev} got={prevh}")
                return 1

            content = as_text(content_raw)
            calc = sha256_hex(("" if prev is None else prev) + content)
            if calc != chainh:
                print("status: FAIL")
                print(f"reason: chain_hash_mismatch id={i} expected={chainh} calc={calc}")
                return 1

            if typ == "daily_signature":
                try:
                    obj = json.loads(content)
                    mc = obj["message_canonical"]
                    sig = bytes.fromhex(obj["signature_hex"])
                    pub.verify(sig, mc.encode("utf-8"))
                except Exception as e:
                    print("status: FAIL")
                    print(f"reason: signature_invalid id={i} err={e}")
                    return 1

            prev = chainh

        final_chain_hash = rows[-1][3] if rows else None
        print("status: OK")
        print("rows_verified:", len(rows))
        print("final_chain_hash:", final_chain_hash)
        return 0
    finally:
        con.close()

if __name__ == "__main__":
    raise SystemExit(main())