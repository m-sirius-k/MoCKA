r"""
Phase15 Audit Scan (deterministic, immutable governance)
date: 2026-02-24

note:
- Governance DB: READ ONLY (never mutated)
- Governance schema: single ledger table "governance_ledger_event"
- Phase15 audits only event_types that actually exist in governance ledger (noise-free)
- Integrity DB: may write ONLY reconciliation_log
- ANCHOR_PROOF: delegates to Phase16 verifier via src.mocka_integrity.phase15_bridge
- No enforcement. Always logs both OK and NG.

governance event_types (as of 2026-02-24):
- GOVERNANCE_GENESIS
- OPERATION_START
- PHASE_TRANSITION
- CLASSIFICATION_CHANGE_DECISION
- TIP_RESELECT_DECISION
- QUARANTINE_ACTION_DECISION
- PROOF_ACTION_EXECUTED

environment:
- MOCKA_GOV_DB               optional (default kernel governance db)
- MOCKA_INTEGRITY_DB         optional (default: infield/phase16/db/integrity.db)
- MOCKA_PHASE16_PUBKEY_PATH  required for crypto verification
- MOCKA_FINAL_CHAIN_HASH     optional override for ANCHOR_PROOF target
"""

from __future__ import annotations

import json
import os
import sqlite3
import sys
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple
from urllib.parse import quote
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_REPO_ROOT = _THIS_FILE.parent.parent  # MoCKA/
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.mocka_integrity.phase15_bridge import phase15_anchor_proof_check
from src.mocka_integrity.integrity_db import IntegrityDBConfig, connect_rw, connect_ro, table_exists_ro


DEFAULT_GOV_DB = str((_REPO_ROOT / "mocka-governance-kernel" / "governance" / "governance.db").resolve())
LEDGER_TABLE = "governance_ledger_event"

GOV_EVENT_TYPES: List[str] = [
    "GOVERNANCE_GENESIS",
    "OPERATION_START",
    "PHASE_TRANSITION",
    "CLASSIFICATION_CHANGE_DECISION",
    "TIP_RESELECT_DECISION",
    "QUARANTINE_ACTION_DECISION",
    "PROOF_ACTION_EXECUTED",
]

AUDIT_EVENT_TYPES: List[str] = GOV_EVENT_TYPES + ["ANCHOR_PROOF"]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _abs(path_str: str) -> str:
    p = Path(path_str)
    if not p.is_absolute():
        p = (_REPO_ROOT / p).resolve()
    return str(p)


def _sqlite_ro_uri(path_str: str) -> str:
    abs_path = Path(_abs(path_str))
    posix = abs_path.as_posix()
    return "file:" + quote(posix) + "?mode=ro"


def _connect_gov_ro(db_path: str) -> sqlite3.Connection:
    uri = _sqlite_ro_uri(db_path)
    conn = sqlite3.connect(uri, uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_reconciliation_log(cfg: IntegrityDBConfig) -> None:
    conn = connect_rw(cfg)
    try:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS reconciliation_log (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              created_utc TEXT NOT NULL,
              event_type TEXT NOT NULL,
              status TEXT NOT NULL,
              reason TEXT NOT NULL,
              detail_json TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_reconciliation_log_created
              ON reconciliation_log(created_utc);
            CREATE INDEX IF NOT EXISTS idx_reconciliation_log_event_type
              ON reconciliation_log(event_type);
            """
        )
        conn.commit()
    finally:
        conn.close()


def _log_result(cfg: IntegrityDBConfig, event_type: str, status: str, reason: str, detail: Dict[str, Any]) -> None:
    conn = connect_rw(cfg)
    try:
        conn.execute(
            "INSERT INTO reconciliation_log(created_utc, event_type, status, reason, detail_json) VALUES (?, ?, ?, ?, ?)",
            (_utc_now_iso(), event_type, status, reason, json.dumps(detail, ensure_ascii=False, sort_keys=True)),
        )
        conn.commit()
    finally:
        conn.close()


def _gov_db_exists(gov_db_path: str) -> bool:
    return os.path.exists(_abs(gov_db_path))


def _gov_table_exists(gov_db_path: str, table: str) -> bool:
    conn = _connect_gov_ro(gov_db_path)
    try:
        cur = conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name=? LIMIT 1",
            (table,),
        )
        return cur.fetchone() is not None
    finally:
        conn.close()


def _ledger_count_by_event_type(gov_db_path: str, event_type: str) -> Tuple[bool, int, Dict[str, Any]]:
    conn = _connect_gov_ro(gov_db_path)
    try:
        cur = conn.execute(f"SELECT COUNT(1) AS n FROM {LEDGER_TABLE} WHERE event_type = ?", (event_type,))
        n = int(cur.fetchone()["n"])
        return True, n, {"column": "event_type"}
    except sqlite3.OperationalError as e:
        return False, 0, {"reason": "QUERY_FAILED", "error": str(e)}
    finally:
        conn.close()


def _check_gov_event_presence(gov_db_path: str, event_type: str) -> Tuple[str, str, Dict[str, Any]]:
    if not _gov_table_exists(gov_db_path, LEDGER_TABLE):
        return "NG", "MISSING_LEDGER_TABLE", {"table": LEDGER_TABLE, "db": _abs(gov_db_path)}

    ok, n, info = _ledger_count_by_event_type(gov_db_path, event_type)
    if not ok:
        return "NG", info.get("reason", "QUERY_FAILED"), {"detail": info, "db": _abs(gov_db_path)}
    if n <= 0:
        return "NG", "MISSING_EVENT_ROWS", {"event_type": event_type, "count": n, "db": _abs(gov_db_path), **info}
    return "OK", "EVENT_ROWS_PRESENT", {"event_type": event_type, "count": n, "db": _abs(gov_db_path), **info}


def _infer_final_chain_hash_from_integrity(integrity_db_path: str) -> Tuple[bool, str, Dict[str, Any]]:
    cfg = IntegrityDBConfig(db_path=integrity_db_path)
    try:
        conn = connect_ro(cfg)
        try:
            if not table_exists_ro(conn, "proof_anchor"):
                return False, "", {"reason": "MISSING_TABLE", "table": "proof_anchor", "db": cfg.db_path}
            cur = conn.execute("SELECT final_chain_hash FROM proof_anchor ORDER BY created_utc DESC LIMIT 1")
            row = cur.fetchone()
            if row is None:
                return False, "", {"reason": "MISSING_ANCHOR", "db": cfg.db_path}
            return True, row["final_chain_hash"], {"db": cfg.db_path}
        finally:
            conn.close()
    except Exception as e:
        return False, "", {"reason": "EXCEPTION", "error": str(e)}


def _check_anchor_proof(integrity_db_path: str, pubkey_path: str) -> Tuple[str, str, Dict[str, Any]]:
    if not pubkey_path:
        return "NG", "MISSING_PUBKEY", {"env": "MOCKA_PHASE16_PUBKEY_PATH"}

    final_chain_hash = os.environ.get("MOCKA_FINAL_CHAIN_HASH", "").strip()
    if not final_chain_hash:
        ok, inferred, info = _infer_final_chain_hash_from_integrity(integrity_db_path)
        if not ok:
            return "NG", info.get("reason", "INFER_FAILED"), info
        final_chain_hash = inferred

    out = phase15_anchor_proof_check(
        final_chain_hash=final_chain_hash,
        integrity_db_path=integrity_db_path,
        public_key_path=pubkey_path,
    )
    return out.get("status", "NG"), out.get("reason", "UNKNOWN"), out.get("detail", {})


def main() -> int:
    gov_db = os.environ.get("MOCKA_GOV_DB", "").strip() or DEFAULT_GOV_DB
    if not _gov_db_exists(gov_db):
        summary = {"status": "NG", "reason": "MISSING_GOV_DB", "detail": {"gov_db": _abs(gov_db)}}
        print(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2))
        return 2

    integrity_db = os.environ.get("MOCKA_INTEGRITY_DB", "").strip() or None
    pubkey_path = os.environ.get("MOCKA_PHASE16_PUBKEY_PATH", "").strip()

    cfg = IntegrityDBConfig(db_path=integrity_db) if integrity_db else IntegrityDBConfig()
    _ensure_reconciliation_log(cfg)

    results: List[Dict[str, Any]] = []
    for et in AUDIT_EVENT_TYPES:
        if et == "ANCHOR_PROOF":
            status, reason, detail = _check_anchor_proof(cfg.db_path, pubkey_path)
        else:
            status, reason, detail = _check_gov_event_presence(gov_db, et)

        _log_result(cfg, et, status, reason, detail)
        results.append({"event_type": et, "status": status, "reason": reason, "detail": detail})

    summary = {
        "status": "OK",
        "created_utc": _utc_now_iso(),
        "gov_db": _abs(gov_db),
        "integrity_db": cfg.db_path,
        "results": results,
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True, indent=2))

    all_ok = all(r["status"] == "OK" for r in results)
    return 0 if all_ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
