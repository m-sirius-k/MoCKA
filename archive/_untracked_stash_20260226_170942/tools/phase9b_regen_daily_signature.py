# C:\Users\sirok\MoCKA\tools\phase9b_regen_daily_signature.py
# NOTE: Phase9-B 修復。id=2削除後に、id=5 を宇宙端として daily_signature を再生成し INSERT する。
# NOTE: schema_version 等の NOT NULL カラムは「anchor行(id=5)の値」を継承して埋める。
# NOTE: 署名対象は message_canonical（UTF-8文字列）。JSONは sort_keys=True + separators=(",",":") で固定。
# NOTE: chain_hash は SHA256(prev_chain_hash + canonical_event_content_json) を UTF-8 で計算（prev_chain_hashはhex文字列のまま連結）。

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
    # dt.datetime.utcnow() の非推奨警告が出ても動作はする。必要なら将来 datetime.UTC に移行。
    return dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


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


def table_info(cur: sqlite3.Cursor, table: str) -> List[Tuple[Any, ...]]:
    cur.execute(f"PRAGMA table_info({table})")
    return cur.fetchall()


def fetch_row(cur: sqlite3.Cursor, sql: str, params: Tuple[Any, ...]) -> Tuple[Any, ...]:
    cur.execute(sql, params)
    row = cur.fetchone()
    if row is None:
        raise RuntimeError("expected row not found")
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=DEFAULT_DB)
    ap.add_argument("--privkey", default=DEFAULT_PRIVKEY)
    ap.add_argument("--anchor-id", type=int, default=5)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(args.db):
        raise FileNotFoundError(args.db)
    if not os.path.exists(args.privkey):
        raise FileNotFoundError(args.privkey)

    con = sqlite3.connect(args.db)
    try:
        cur = con.cursor()

        info = table_info(cur, "audit_ledger_event")
        cols = [r[1] for r in info]  # name
        notnull = {r[1]: bool(r[3]) for r in info}  # name -> notnull(0/1)
        # r: (cid, name, type, notnull, dflt_value, pk)

        required = {"event_type", "event_content", "prev_chain_hash", "chain_hash"}
        missing = sorted(list(required - set(cols)))
        if missing:
            raise RuntimeError(f"audit_ledger_event missing columns: {missing}")

        # anchor行を丸ごと取得（後で NOT NULL の継承元にする）
        cur.execute("SELECT * FROM audit_ledger_event WHERE id=?", (args.anchor_id,))
        anchor_full = cur.fetchone()
        if anchor_full is None:
            raise RuntimeError("anchor row not found")

        anchor_map = dict(zip(cols, anchor_full))

        # 宇宙端
        prev_chain_hash = anchor_map["chain_hash"]

        # daily_signature 再生成
        message_canonical_obj: Dict[str, Any] = {
            "kind": "daily_signature",
            "final_chain_hash": prev_chain_hash,
            "ts_utc": utc_now_iso(),
            "note": "Phase9-B regen after placeholder purge",
        }
        message_canonical = canonical_json(message_canonical_obj)

        priv = load_ed25519_private_key(args.privkey)
        signature_hex = priv.sign(message_canonical.encode("utf-8")).hex()

        event_content_obj: Dict[str, Any] = {
            "message_canonical": message_canonical,
            "signature_hex": signature_hex,
        }
        event_content_json = canonical_json(event_content_obj)

        new_chain_hash = sha256_hex(prev_chain_hash + event_content_json)

        # 基本カラム
        insert = {
            "event_type": "daily_signature",
            "event_content": event_content_json,
            "prev_chain_hash": prev_chain_hash,
            "chain_hash": new_chain_hash,
        }

        # NOT NULL かつデフォルト無しっぽい追加カラムを anchor から継承して埋める
        # ただし id(PK) は除外。chain/hashは上で埋めた。event系も上で埋めた。
        protected = {"id", "event_type", "event_content", "prev_chain_hash", "chain_hash"}
        for c in cols:
            if c in protected:
                continue
            if notnull.get(c, False):
                # NULL だと落ちる可能性が高いので継承
                if c not in insert:
                    insert[c] = anchor_map.get(c)

        # created_at/updated_at があれば現在時刻に更新（NOT NULLなら上の継承よりこちらを優先）
        now = utc_now_iso()
        if "created_at" in cols:
            insert["created_at"] = now
        if "updated_at" in cols:
            insert["updated_at"] = now

        # schema_version があるなら明示的に anchor から継承（今回の失敗点）
        if "schema_version" in cols and "schema_version" not in insert:
            insert["schema_version"] = anchor_map.get("schema_version")

        insert_cols = list(insert.keys())
        insert_vals = [insert[c] for c in insert_cols]
        sql = f"INSERT INTO audit_ledger_event ({','.join(insert_cols)}) VALUES ({','.join(['?']*len(insert_cols))})"

        print("ANCHOR_ID=", args.anchor_id)
        print("ANCHOR_CHAIN_HASH=", prev_chain_hash)
        print("MESSAGE_CANONICAL=", message_canonical)
        print("EVENT_CONTENT_JSON=", event_content_json)
        print("NEW_CHAIN_HASH=", new_chain_hash)
        print("INSERT_COLS=", insert_cols)

        if args.dry_run:
            print("DRY_RUN: no insert performed")
            return 0

        cur.execute(sql, tuple(insert_vals))
        con.commit()
        new_id = cur.lastrowid
        print("INSERT_OK: new_id=", new_id)

        cur.execute("SELECT id,event_type,prev_chain_hash,chain_hash FROM audit_ledger_event WHERE id=?", (new_id,))
        print("INSERT_ROW=", cur.fetchone())
        return 0
    finally:
        con.close()


if __name__ == "__main__":
    raise SystemExit(main())