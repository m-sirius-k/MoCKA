# C:\Users\sirok\MoCKA\tools\phase9b_rebuild_from_id4.py
# NOTE: Phase9-B A確立用。id=1(placeholder混入でchain不整合)を除去し、id=4をgenesisとして一本鎖を再構築する。
# NOTE: chain_hash = SHA256(prev_chain_hash + event_content_json_text) をUTF-8で計算（prev_chain_hashはhex文字列を連結）。
# NOTE: daily_signature は final_chain_hash が変わるので削除→再生成→INSERT。
# NOTE: INSERT時のNOT NULL列（schema_version等）はanchor(id=5)の値を継承して埋める。

import argparse
import datetime as dt
import hashlib
import json
import os
import sqlite3
from typing import Any, Dict, List, Tuple, Optional

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

DEFAULT_DB = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"
DEFAULT_PRIVKEY = r"C:\Users\sirok\MoCKA\secrets\ed25519\ed25519_private.key"

def utc_now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def load_ed25519_private_key(path: str) -> Ed25519PrivateKey:
    with open(path, "rb") as f:
        data = f.read()
    if b"BEGIN" in data[:64]:
        key = serialization.load_pem_private_key(data, password=None)
        if not isinstance(key, Ed25519PrivateKey):
            raise TypeError("private key is not Ed25519")
        return key
    raw = data.strip()
    if len(raw) != 32:
        raise ValueError(f"RAW private key must be 32 bytes, got {len(raw)} bytes")
    return Ed25519PrivateKey.from_private_bytes(raw)

def pragma_table_info(cur: sqlite3.Cursor, table: str) -> List[Tuple[Any, ...]]:
    cur.execute(f"PRAGMA table_info({table})")
    return cur.fetchall()

def fetch_one(cur: sqlite3.Cursor, sql: str, params: Tuple[Any, ...]) -> Tuple[Any, ...]:
    cur.execute(sql, params)
    row = cur.fetchone()
    if row is None:
        raise RuntimeError(f"row not found: {sql} {params}")
    return row

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--privkey", default=DEFAULT_PRIVKEY)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.db):
        raise FileNotFoundError(args.db)
    if not os.path.exists(args.privkey):
        raise FileNotFoundError(args.privkey)

    con = sqlite3.connect(args.db)
    try:
        cur = con.cursor()
        info = pragma_table_info(cur, "audit_ledger_event")
        cols = [r[1] for r in info]
        notnull = {r[1]: bool(r[3]) for r in info}

        need = {"id","event_type","event_content","prev_chain_hash","chain_hash"}
        miss = sorted(list(need - set(cols)))
        if miss:
            raise RuntimeError(f"missing columns: {miss}")

        # 現状表示
        cur.execute("SELECT id,event_type,prev_chain_hash,chain_hash FROM audit_ledger_event ORDER BY id ASC")
        before = cur.fetchall()
        print("BEFORE=")
        for r in before:
            print(r)

        # id=4,5 のevent_contentを取得（文字列として扱う）
        c4 = fetch_one(cur, "SELECT event_content FROM audit_ledger_event WHERE id=4", ())[0]
        c5 = fetch_one(cur, "SELECT event_content FROM audit_ledger_event WHERE id=5", ())[0]
        if not isinstance(c4, str):
            c4 = json.dumps(c4, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        if not isinstance(c5, str):
            c5 = json.dumps(c5, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

        # 再計算：id=4 をgenesis（prev=None）
        new_prev4: Optional[str] = None
        new_chain4 = sha256_hex("" + c4)

        # id=5 は id=4 の後ろへ
        new_prev5 = new_chain4
        new_chain5 = sha256_hex(new_prev5 + c5)

        # 既存 daily_signature を全削除（idに依存しない）
        cur.execute("SELECT COUNT(*) FROM audit_ledger_event WHERE event_type='daily_signature'")
        daily_count = cur.fetchone()[0]

        # anchor(id=5) の NOT NULL を継承して新daily_signatureをINSERT
        cur.execute("SELECT * FROM audit_ledger_event WHERE id=5")
        anchor_full = cur.fetchone()
        if anchor_full is None:
            raise RuntimeError("anchor id=5 not found")
        anchor_map = dict(zip(cols, anchor_full))

        priv = load_ed25519_private_key(args.privkey)

        message_canonical_obj: Dict[str, Any] = {
            "kind": "daily_signature",
            "final_chain_hash": new_chain5,
            "ts_utc": utc_now_iso(),
            "note": "Phase9-B rebuild from id=4 genesis (id=1 purged)",
        }
        message_canonical = json.dumps(message_canonical_obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        signature_hex = priv.sign(message_canonical.encode("utf-8")).hex()

        event_content_obj: Dict[str, Any] = {
            "message_canonical": message_canonical,
            "signature_hex": signature_hex,
        }
        event_content_json = json.dumps(event_content_obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        new_chain_sig = sha256_hex(new_chain5 + event_content_json)

        insert: Dict[str, Any] = {
            "event_type": "daily_signature",
            "event_content": event_content_json,
            "prev_chain_hash": new_chain5,
            "chain_hash": new_chain_sig,
        }

        protected = {"id","event_type","event_content","prev_chain_hash","chain_hash"}
        for c in cols:
            if c in protected:
                continue
            if notnull.get(c, False):
                if c not in insert:
                    insert[c] = anchor_map.get(c)

        now = utc_now_iso()
        if "created_at" in cols:
            insert["created_at"] = now
        if "updated_at" in cols:
            insert["updated_at"] = now

        print("PLAN=")
        print("DELETE id=1")
        print("UPDATE id=4 prev=NULL chain=", new_chain4)
        print("UPDATE id=5 prev=", new_prev5, " chain=", new_chain5)
        print("DELETE daily_signature count=", daily_count)
        print("INSERT daily_signature prev=", new_chain5, " chain=", new_chain_sig)
        print("INSERT_COLS=", list(insert.keys()))

        if args.dry_run:
            print("DRY_RUN: no changes")
            return 0

        # 適用
        cur.execute("DELETE FROM audit_ledger_event WHERE id=1")

        if "updated_at" in cols:
            cur.execute("UPDATE audit_ledger_event SET prev_chain_hash=NULL, chain_hash=?, updated_at=? WHERE id=4", (new_chain4, utc_now_iso()))
            cur.execute("UPDATE audit_ledger_event SET prev_chain_hash=?, chain_hash=?, updated_at=? WHERE id=5", (new_prev5, new_chain5, utc_now_iso()))
        else:
            cur.execute("UPDATE audit_ledger_event SET prev_chain_hash=NULL, chain_hash=? WHERE id=4", (new_chain4,))
            cur.execute("UPDATE audit_ledger_event SET prev_chain_hash=?, chain_hash=? WHERE id=5", (new_prev5, new_chain5))

        cur.execute("DELETE FROM audit_ledger_event WHERE event_type='daily_signature'")

        insert_cols = list(insert.keys())
        insert_vals = [insert[c] for c in insert_cols]
        sql = f"INSERT INTO audit_ledger_event ({','.join(insert_cols)}) VALUES ({','.join(['?']*len(insert_cols))})"
        cur.execute(sql, tuple(insert_vals))
        con.commit()
        new_id = cur.lastrowid
        print("APPLY_OK new_daily_signature_id=", new_id)

        cur.execute("SELECT id,event_type,prev_chain_hash,chain_hash FROM audit_ledger_event ORDER BY id ASC")
        after = cur.fetchall()
        print("AFTER=")
        for r in after:
            print(r)

        return 0
    finally:
        con.close()

if __name__ == "__main__":
    raise SystemExit(main())