# C:\Users\sirok\MoCKA\tools\phase9b_rebase_chain.py
# NOTE: Phase9-B rebase fix.
# NOTE: id=2削除により、id=4のprev_chain_hashが欠損したため、id=1 -> id=4 -> id=5 の一本鎖へ付け替える。
# NOTE: id=7(daily_signature) は final_chain_hash が旧id=5 chain に依存しているため削除し、再生成して挿入する。
# NOTE: chain_hash は SHA256(prev_chain_hash + event_content_json) をUTF-8で計算（prev_chain_hashはhex文字列連結）。

import argparse
import datetime as dt
import hashlib
import json
import os
import sqlite3
from typing import Any, Dict, List, Tuple

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

DEFAULT_DB = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"
DEFAULT_PRIVKEY = r"C:\Users\sirok\MoCKA\secrets\ed25519\ed25519_private.key"


def utc_now_iso() -> str:
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


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
        raise RuntimeError(f"row not found for query: {sql} params={params}")
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--privkey", default=DEFAULT_PRIVKEY)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--keep-ts", action="store_true", help="created_at/updated_at を更新しない（既存値維持）")
    args = ap.parse_args()

    if not os.path.exists(args.db):
        raise FileNotFoundError(args.db)
    if not os.path.exists(args.privkey):
        raise FileNotFoundError(args.privkey)

    con = sqlite3.connect(args.db)
    try:
        cur = con.cursor()

        info = pragma_table_info(cur, "audit_ledger_event")
        cols = [r[1] for r in info]  # name
        notnull = {r[1]: bool(r[3]) for r in info}

        required = {"id", "event_type", "event_content", "prev_chain_hash", "chain_hash"}
        missing = sorted(list(required - set(cols)))
        if missing:
            raise RuntimeError(f"missing columns: {missing}")

        # 現状確認
        cur.execute("SELECT id,event_type,prev_chain_hash,chain_hash FROM audit_ledger_event ORDER BY id ASC")
        rows = cur.fetchall()
        print("BEFORE_ROWS=")
        for r in rows:
            print(r)

        # genesis (id=1)
        id1 = fetch_one(cur, "SELECT chain_hash FROM audit_ledger_event WHERE id=1", ())
        chain1 = id1[0]
        if chain1 is None:
            raise RuntimeError("id=1 chain_hash is None")

        # id=4 の event_content を取り出し、prev を chain1 に付け替えて chain を再計算
        id4 = fetch_one(cur, "SELECT event_content FROM audit_ledger_event WHERE id=4", ())
        content4 = id4[0]
        if not isinstance(content4, str):
            content4 = canonical_json(content4)
        new_prev4 = chain1
        new_chain4 = sha256_hex(new_prev4 + content4)

        # id=5 同様
        id5 = fetch_one(cur, "SELECT event_content FROM audit_ledger_event WHERE id=5", ())
        content5 = id5[0]
        if not isinstance(content5, str):
            content5 = canonical_json(content5)
        new_prev5 = new_chain4
        new_chain5 = sha256_hex(new_prev5 + content5)

        # id=7 は削除予定（存在チェック）
        cur.execute("SELECT COUNT(*) FROM audit_ledger_event WHERE id=7")
        has7 = cur.fetchone()[0] == 1

        # 新 daily_signature を生成して INSERT（prev=new_chain5）
        priv = load_ed25519_private_key(args.privkey)

        message_canonical_obj: Dict[str, Any] = {
            "kind": "daily_signature",
            "final_chain_hash": new_chain5,
            "ts_utc": utc_now_iso(),
            "note": "Phase9-B rebase regen after id2 purge",
        }
        message_canonical = canonical_json(message_canonical_obj)
        signature_hex = priv.sign(message_canonical.encode("utf-8")).hex()

        event_content_obj: Dict[str, Any] = {
            "message_canonical": message_canonical,
            "signature_hex": signature_hex,
        }
        event_content_json = canonical_json(event_content_obj)
        new_chain_sig = sha256_hex(new_chain5 + event_content_json)

        # INSERT 用に anchor(id=5) の NOT NULL 値を継承
        cur.execute("SELECT * FROM audit_ledger_event WHERE id=5")
        anchor_full = cur.fetchone()
        if anchor_full is None:
            raise RuntimeError("anchor id=5 not found")
        anchor_map = dict(zip(cols, anchor_full))

        insert: Dict[str, Any] = {
            "event_type": "daily_signature",
            "event_content": event_content_json,
            "prev_chain_hash": new_chain5,
            "chain_hash": new_chain_sig,
        }

        protected = {"id", "event_type", "event_content", "prev_chain_hash", "chain_hash"}
        for c in cols:
            if c in protected:
                continue
            if notnull.get(c, False):
                if c not in insert:
                    insert[c] = anchor_map.get(c)

        if not args.keep_ts:
            now = utc_now_iso()
            if "created_at" in cols:
                insert["created_at"] = now
            if "updated_at" in cols:
                insert["updated_at"] = now

        print("PLAN=")
        print("UPDATE id=4 prev->", new_prev4)
        print("UPDATE id=4 chain->", new_chain4)
        print("UPDATE id=5 prev->", new_prev5)
        print("UPDATE id=5 chain->", new_chain5)
        print("DELETE id=7 ->", has7)
        print("INSERT daily_signature prev->", new_chain5)
        print("INSERT daily_signature chain->", new_chain_sig)
        print("INSERT_COLS=", list(insert.keys()))

        if args.dry_run:
            print("DRY_RUN: no changes")
            return 0

        # 実更新
        # id=4
        if not args.keep_ts and "updated_at" in cols:
            cur.execute(
                "UPDATE audit_ledger_event SET prev_chain_hash=?, chain_hash=?, updated_at=? WHERE id=4",
                (new_prev4, new_chain4, utc_now_iso()),
            )
        else:
            cur.execute(
                "UPDATE audit_ledger_event SET prev_chain_hash=?, chain_hash=? WHERE id=4",
                (new_prev4, new_chain4),
            )

        # id=5
        if not args.keep_ts and "updated_at" in cols:
            cur.execute(
                "UPDATE audit_ledger_event SET prev_chain_hash=?, chain_hash=?, updated_at=? WHERE id=5",
                (new_prev5, new_chain5, utc_now_iso()),
            )
        else:
            cur.execute(
                "UPDATE audit_ledger_event SET prev_chain_hash=?, chain_hash=? WHERE id=5",
                (new_prev5, new_chain5),
            )

        # id=7 delete
        if has7:
            cur.execute("DELETE FROM audit_ledger_event WHERE id=7")

        # insert new daily_signature
        insert_cols = list(insert.keys())
        insert_vals = [insert[c] for c in insert_cols]
        sql = f"INSERT INTO audit_ledger_event ({','.join(insert_cols)}) VALUES ({','.join(['?']*len(insert_cols))})"
        cur.execute(sql, tuple(insert_vals))

        con.commit()
        new_id = cur.lastrowid
        print("APPLY_OK new_id=", new_id)

        cur.execute("SELECT id,event_type,prev_chain_hash,chain_hash FROM audit_ledger_event ORDER BY id ASC")
        rows2 = cur.fetchall()
        print("AFTER_ROWS=")
        for r in rows2:
            print(r)

        return 0
    finally:
        con.close()


if __name__ == "__main__":
    raise SystemExit(main())