import glob
import json
import os
import sys
import sqlite3
import hashlib
from datetime import datetime, timezone
from typing import Any

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from src.mocka_audit.contract_v1 import AuditEventInput, derive_event

CANONICAL_DB = r"C:\Users\sirok\MoCKA\audit\ed25519\audit.db"
OUTBOX_DIR = os.path.join(REPO_ROOT, "outbox")
TIP = "cc009711c19a8a9358bd282446f3cbcd3b834200ac5e7630e720bb820954b121"
CONTRACT_VERSION = "mocka.audit.v1"


def _pick_latest_note_event() -> str:
    files = glob.glob(os.path.join(OUTBOX_DIR, "*_event.json"))
    if not files:
        raise FileNotFoundError("no outbox *_event.json found")
    files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    return files[0]


def _load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _compact_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def _sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _parse_ts(ts_val: Any) -> datetime:
    if isinstance(ts_val, (int, float)):
        t = float(ts_val)
        if t > 1e12:
            t = t / 1000.0
        return datetime.fromtimestamp(t, tz=timezone.utc).astimezone()
    if isinstance(ts_val, str):
        s = ts_val.strip()
        try:
            s2 = s.replace("Z", "+00:00")
            dt = datetime.fromisoformat(s2)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc).astimezone()
            else:
                dt = dt.astimezone()
            return dt
        except Exception:
            pass
    return datetime.now().astimezone()


def _insert_ledger_event(db_path: str, event_id: str, previous_event_id: str, chain_hash: str, event_content: str, created_at: str) -> None:
    # DB schema confirmed:
    # event_id TEXT PK
    # chain_hash TEXT NOT NULL
    # previous_event_id TEXT NOT NULL DEFAULT 'GENESIS'
    # event_content TEXT NOT NULL
    # contract_version TEXT NOT NULL
    # created_at TEXT NOT NULL
    with sqlite3.connect(db_path) as conn:
        sql = (
            "INSERT INTO audit_ledger_event "
            "(event_id, chain_hash, previous_event_id, event_content, contract_version, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?);"
        )
        conn.execute(sql, (event_id, chain_hash, previous_event_id, event_content, CONTRACT_VERSION, created_at))
        conn.commit()


def main(argv: list[str]) -> int:
    src_json = argv[1] if len(argv) >= 2 else _pick_latest_note_event()
    obj = _load_json(src_json)
    if not isinstance(obj, dict):
        raise ValueError("note event json top-level is not dict")

    ts_local = _parse_ts(obj.get("ts"))
    event_kind = str(obj.get("event_kind") or "note")

    packet = _compact_json(obj)
    h = _sha256_hex(packet)

    target_path = "outbox:" + os.path.basename(src_json)

    inp = AuditEventInput(
        ts_local=ts_local,
        event_kind=event_kind,
        target_path=target_path,
        sha256_source=h,
        sha256_after=h,
        contract_version=CONTRACT_VERSION,
    )

    d = derive_event(inp, previous_event_id=TIP)

    # created_at は DB 用に ISO8601 文字列で保存（ローカル時刻、tz付き）
    created_at = ts_local.isoformat()

    _insert_ledger_event(
        db_path=CANONICAL_DB,
        event_id=d.event_id,
        previous_event_id=TIP,
        chain_hash=d.chain_hash,
        event_content=d.event_content,
        created_at=created_at,
    )

    print("OK: derived+accepted note event")
    print("src_json=" + src_json)
    print("event_kind=" + event_kind)
    print("created_at=" + created_at)
    print("event_id=" + d.event_id)
    print("previous_event_id=" + TIP)
    print("chain_hash=" + d.chain_hash)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
