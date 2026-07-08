"""
TODO_428: MOCKA_OVERVIEW_CURRENT_GENERATION

一次データ(MOCKA_TODO_ACTIVE/ARCHIVE.json, decision_ledger.jsonl, mocka_events.db,
governance/anchor_record.json)から data/MOCKA_OVERVIEW_CURRENT.json を機械的に再集計する。

legacyの C:\\Users\\sirok\\MOCKA_OVERVIEW.json、および data/MOCKA_OVERVIEW.json
(export_for_cloudflare.pyのミラー)は読み書きしない。本文(session_history/next_actions/
current_issues相当)は自由記述ではなく、一次データから機械的に集計した値のみとする。
"""
import json
import hashlib
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

MOCKA_ROOT = Path(r"C:\Users\sirok\MoCKA")
DATA_DIR = MOCKA_ROOT / "data"

TODO_ACTIVE_PATH = DATA_DIR / "MOCKA_TODO_ACTIVE.json"
TODO_ARCHIVE_PATH = DATA_DIR / "MOCKA_TODO_ARCHIVE.json"
DECISION_LEDGER_PATH = DATA_DIR / "decisions" / "decision_ledger.jsonl"
EVENTS_DB_PATH = DATA_DIR / "mocka_events.db"
ANCHOR_RECORD_PATH = MOCKA_ROOT / "governance" / "anchor_record.json"
OUTPUT_PATH = DATA_DIR / "MOCKA_OVERVIEW_CURRENT.json"

GENERATOR_VERSION = "1.0"
CANONICAL_STATUSES = ("未着手", "進行中", "完了", "保留", "廃止")


def _sha256(path: Path):
    if not path.exists():
        return None
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _normalize_status_bucket(status):
    if not status:
        return "unknown"
    for canonical in CANONICAL_STATUSES:
        if status.startswith(canonical):
            return canonical
    return "other"


def _load_todo_summary():
    """TODO_384正規5値へ正規化して集計し、ACTIVE.completedバケットの
    status不整合(チェック1: TODO整合のスコープ内実装)を検知する。"""
    active = json.loads(TODO_ACTIVE_PATH.read_text(encoding="utf-8"))
    archive = json.loads(TODO_ARCHIVE_PATH.read_text(encoding="utf-8"))

    summary = Counter()
    warnings = []

    for entry in active.get("todos", []):
        summary[_normalize_status_bucket(entry.get("status"))] += 1

    for entry in active.get("completed", []):
        bucket = _normalize_status_bucket(entry.get("status"))
        summary[bucket] += 1
        if bucket != "完了":
            warnings.append({
                "check": "todo_consistency",
                "todo_id": entry.get("id"),
                "detail": f"ACTIVE.completedに分類されているが status='{entry.get('status')}'(完了以外)",
            })

    for entry in archive.get("completed", []):
        summary[_normalize_status_bucket(entry.get("status"))] += 1

    return dict(summary), warnings


def _load_decision_summary():
    if not DECISION_LEDGER_PATH.exists():
        return {"count": 0, "latest": None}
    lines = [ln for ln in DECISION_LEDGER_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]
    latest_brief = None
    if lines:
        latest = json.loads(lines[-1])
        latest_brief = {
            "decision_id": latest.get("decision_id"),
            "title": latest.get("title"),
            "approved_at": latest.get("approved_at"),
        }
    return {"count": len(lines), "latest": latest_brief}


def _load_event_summary():
    if not EVENTS_DB_PATH.exists():
        return {"count": 0, "latest_timestamp": None}
    con = sqlite3.connect(str(EVENTS_DB_PATH))
    try:
        count = con.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        # when_ts列には文字化け/破損データ(既知事象、TODO_423参照)が混在するため、
        # 文字列比較になるORDER BY when_ts DESCは使わず、挿入順(rowid)で最新を取る
        # (export_for_cloudflare.pyのexport_events()と同じ方式)。
        latest = con.execute("SELECT when_ts FROM events ORDER BY rowid DESC LIMIT 1").fetchone()
    finally:
        con.close()
    return {"count": count, "latest_timestamp": latest[0] if latest else None}


def _load_seal_status():
    if not ANCHOR_RECORD_PATH.exists():
        return {}
    anchor = json.loads(ANCHOR_RECORD_PATH.read_text(encoding="utf-8"))
    return {
        "anchor_type": anchor.get("anchor_type"),
        "sealed_at_utc": anchor.get("sealed_at_utc"),
        "sealed_summary_hash": anchor.get("sealed_summary_hash"),
    }


def generate():
    """一次データを再集計して結果dictを返す(ファイルへの書込は行わない)。"""
    todo_summary, todo_warnings = _load_todo_summary()
    return {
        "meta": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generator_version": GENERATOR_VERSION,
            "source_hashes": {
                "todo_active": _sha256(TODO_ACTIVE_PATH),
                "todo_archive": _sha256(TODO_ARCHIVE_PATH),
                "decision_ledger": _sha256(DECISION_LEDGER_PATH),
                "anchor_record": _sha256(ANCHOR_RECORD_PATH),
            },
        },
        "todo_summary": todo_summary,
        "recent_decisions": _load_decision_summary(),
        "recent_events": _load_event_summary(),
        "seal_status": _load_seal_status(),
        "integrity_warnings": todo_warnings,
    }


def write_output(result=None):
    if result is None:
        result = generate()
    OUTPUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return OUTPUT_PATH


if __name__ == "__main__":
    out_path = write_output()
    print(f"[overview_current_generator] wrote {out_path}")
