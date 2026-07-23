"""
Runtime event -> EvidenceRecord 生成経路(Phase8-2)

events.db への接続は読み取り専用モード(sqlite3 URI + mode=ro)で開く。
書き込みが必要な場合(CHANGE_EVENT記録)は、interface/gate_policy.py の
ALLOWED_DIRECT_CHANNELS に定義された "restore" チャネル経由のみで行い、
生のSQL INSERTを直接発行しない(既存Gate機構への責務混在を避けるため)。
"""

import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

MOCKA_ROOT = Path(r"C:\Users\sirok\MoCKA")
DB_PATH = MOCKA_ROOT / "data" / "mocka_events.db"

sys.path.insert(0, str(MOCKA_ROOT))
from governance.write_path.evidence import schema as evidence_schema  # noqa: E402

_INTEGRITY_FILTER = "(data_integrity IN ('normal', 'alt_schema_intentional') OR data_integrity IS NULL)"


def _read_events_readonly():
    """events.dbを読み取り専用接続で開き、既存互換形式のdictリストを返す。"""
    uri = f"file:{DB_PATH.as_posix()}?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    con.row_factory = sqlite3.Row
    try:
        cur = con.execute(
            f"SELECT * FROM events WHERE {_INTEGRITY_FILTER} ORDER BY rowid"
        )
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
    finally:
        con.close()
    return rows


def generate_evidence_record(generated_by: str) -> dict:
    """
    Runtime Observation(events.db全件)から RuntimeEvidenceRecord を組み立てる。
    永続化は行わない(in-memoryでの生成・検証のみ)。
    """
    rows = _read_events_readonly()
    payload = json.dumps(rows, ensure_ascii=False, sort_keys=True).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()

    record = {
        "record_id": f"RER_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{digest[:8]}",
        "source_event_range": {
            "from_event_id": rows[0]["event_id"] if rows else "",
            "to_event_id": rows[-1]["event_id"] if rows else "",
            "event_count": len(rows),
        },
        "hash": digest,
        "hash_method_spec": "sha256_json_sorted_v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_by": generated_by,
        "governance_anchor_hash": None,  # adapter.pyが解決する値。generator単体では未確定
        "immutable": True,
    }

    errors = evidence_schema.validate(record)
    if errors:
        raise ValueError(f"generated RuntimeEvidenceRecord failed validation: {errors}")

    return record


def record_change_event(event_type: str, record_id: str, extra: str = "") -> dict:
    """
    CHANGE_START/CHANGE_DONE相当のイベントを、既存Gate機構(interface/db_helper.py +
    interface/gate_policy.py)の "restore" チャネル経由でevents.dbへ記録するためのフック。

    Phase8-2時点ではこの関数は実装のみ行い、検証実行時には呼び出さない
    (production Generatorへ組み込まれた際に初めて実運用で呼ばれる想定)。
    """
    sys.path.insert(0, str(MOCKA_ROOT / "interface"))
    import db_helper  # noqa: E402

    row = {
        "event_id": db_helper.get_next_event_id(),
        "when": datetime.now(timezone.utc).isoformat(),
        "who_actor": "write_path.runtime.generator",
        "what_type": event_type,
        "where_component": "governance/write_path/runtime/generator.py",
        "where_path": "governance/write_path/runtime/generator.py",
        "why_purpose": "Write Path v1.0 Evidence Record生成に伴う記録",
        "how_trigger": "write_path_generator",
        "title": f"{event_type}: RuntimeEvidenceRecord {record_id}",
        "short_summary": extra,
        "free_note": extra,
    }
    ok = db_helper.write_event(row, channel="restore")
    return {"written": ok, "event_id": row["event_id"]}
