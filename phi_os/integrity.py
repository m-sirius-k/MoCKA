#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
phi_os/integrity.py -- Phase5-2 Event Integrity Framework

Event Signature + Hash Chain + Integrity Verification + Recovery Support
を一体で実装する。Phase5-1/5-1.5でGate Enforcement・Schema Integrity
Hardeningが完了し、events._sourceがGate Policyと一致することは
保証された。本モジュールはその先の"記録後の改ざん検知"を担う。

設計方針:
  - algorithm/signature_versionは固定実装にしない。ALGORITHMS辞書に
    登録し、SIGNATURE_VERSIONを上げるだけで将来のアルゴリズム追加に
    対応できる構造にする。
  - event_signaturesはeventsとは別テーブル（1:1）。既存32カラムの
    eventsテーブルを汚さず、追加的に署名・チェーン情報を持つ。
  - 自動修復は実装しない。診断(diagnose)と修復提案のみを返す。
"""

import hashlib
import json
import sqlite3
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT / "interface"))

SIGNATURE_VERSION = "1.0"

# アルゴリズム登録レジストリ。将来のアルゴリズム追加はここに1行足すだけでよい。
ALGORITHMS = {
    "sha256": hashlib.sha256,
}
DEFAULT_ALGORITHM = "sha256"

# 既知のsignature_version集合（Verificationで不正版を検出するため）
KNOWN_SIGNATURE_VERSIONS = frozenset({"1.0"})

DB_PATH = _REPO_ROOT / "data" / "mocka_events.db"

# 改ざん検知の対象とするevents列（5W1Hコア+内容+変化記録+_source）
SIGNED_FIELDS = (
    "event_id", "when_ts", "who_actor", "what_type",
    "title", "short_summary", "before_state", "after_state",
    "_source", "free_note",
)


def canonical_payload(event_row: dict) -> str:
    """event_rowからSIGNED_FIELDSのみを取り出し、安定した正規JSON文字列を返す"""
    subset = {k: event_row.get(k) for k in SIGNED_FIELDS}
    return json.dumps(subset, ensure_ascii=False, sort_keys=True)


def compute_hash(event_row: dict, previous_hash: str, algorithm: str = DEFAULT_ALGORITHM) -> str:
    """previous_hash + canonical_payload(event_row)からcurrent_hashを計算する"""
    if algorithm not in ALGORITHMS:
        raise ValueError(f"unknown algorithm: {algorithm}")
    hasher = ALGORITHMS[algorithm]()
    canon = previous_hash + "|" + canonical_payload(event_row)
    hasher.update(canon.encode("utf-8"))
    return hasher.hexdigest()


def ensure_signatures_table(conn: sqlite3.Connection) -> None:
    conn.execute('''
        CREATE TABLE IF NOT EXISTS event_signatures (
            event_id          TEXT PRIMARY KEY REFERENCES events(event_id),
            seq               INTEGER NOT NULL UNIQUE,
            timestamp         TEXT NOT NULL,
            previous_hash     TEXT NOT NULL,
            current_hash      TEXT NOT NULL,
            signature_version TEXT NOT NULL,
            algorithm         TEXT NOT NULL
        )
    ''')
    conn.execute(
        'CREATE INDEX IF NOT EXISTS idx_event_signatures_seq ON event_signatures(seq)'
    )


def _last_signature(conn: sqlite3.Connection) -> sqlite3.Row:
    return conn.execute(
        'SELECT * FROM event_signatures ORDER BY seq DESC LIMIT 1'
    ).fetchone()


def sign_event(conn: sqlite3.Connection, event_row: dict,
                algorithm: str = DEFAULT_ALGORITHM) -> dict:
    """
    events挿入直後（同一トランザクション内）に呼び出す。
    event_signaturesに新しいチェーン要素を1件追加し、その内容を返す。
    """
    ensure_signatures_table(conn)
    last = _last_signature(conn)
    seq = (last["seq"] + 1) if last else 1
    previous_hash = last["current_hash"] if last else ""
    current_hash = compute_hash(event_row, previous_hash, algorithm)
    timestamp = event_row.get("when_ts") or event_row.get("when") or ""

    conn.execute(
        'INSERT INTO event_signatures '
        '(event_id, seq, timestamp, previous_hash, current_hash, signature_version, algorithm) '
        'VALUES (?, ?, ?, ?, ?, ?, ?)',
        (event_row.get("event_id"), seq, timestamp, previous_hash,
         current_hash, SIGNATURE_VERSION, algorithm)
    )

    return {
        "event_id": event_row.get("event_id"),
        "seq": seq,
        "timestamp": timestamp,
        "previous_hash": previous_hash,
        "current_hash": current_hash,
        "signature_version": SIGNATURE_VERSION,
        "algorithm": algorithm,
    }


def verify_chain(conn: sqlite3.Connection, start_seq: int = None, end_seq: int = None) -> dict:
    """
    event_signaturesをseq順に走査し、STEP3で要求される全項目を検証する。
    戻り値: {"ok": bool, "checked": int, "anomalies": [ {type, seq, event_id, detail}, ... ]}
    """
    anomalies = []

    where = []
    params = []
    if start_seq is not None:
        where.append("seq >= ?")
        params.append(start_seq)
    if end_seq is not None:
        where.append("seq <= ?")
        params.append(end_seq)
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    rows = conn.execute(
        f'SELECT * FROM event_signatures {where_sql} ORDER BY seq ASC', params
    ).fetchall()

    prev_hash_expected = None
    prev_seq = None
    checked = 0

    for row in rows:
        checked += 1
        seq = row["seq"]
        event_id = row["event_id"]

        # 欠番検出
        if prev_seq is not None and seq != prev_seq + 1:
            anomalies.append({
                "type": "missing_seq", "seq": seq, "event_id": event_id,
                "detail": f"seq gap detected: previous seq={prev_seq}, current seq={seq}",
            })

        # signature_version検証
        if row["signature_version"] not in KNOWN_SIGNATURE_VERSIONS:
            anomalies.append({
                "type": "invalid_signature_version", "seq": seq, "event_id": event_id,
                "detail": f"unknown signature_version: {row['signature_version']}",
            })

        # algorithm検証
        if row["algorithm"] not in ALGORITHMS:
            anomalies.append({
                "type": "invalid_algorithm", "seq": seq, "event_id": event_id,
                "detail": f"unknown algorithm: {row['algorithm']}",
            })
        else:
            # chain break検出（先頭行はprev_hash_expectedがNoneなのでスキップ）
            if prev_hash_expected is not None and row["previous_hash"] != prev_hash_expected:
                anomalies.append({
                    "type": "chain_break", "seq": seq, "event_id": event_id,
                    "detail": "previous_hash does not match prior current_hash",
                })

            # hash一致検証（改ざん検出）— 対応するeventsレコードから再計算
            event_row = conn.execute(
                'SELECT * FROM events WHERE event_id = ?', (event_id,)
            ).fetchone()
            if event_row is None:
                anomalies.append({
                    "type": "missing_event_row", "seq": seq, "event_id": event_id,
                    "detail": "signature exists but events row not found",
                })
            else:
                recomputed = compute_hash(dict(event_row), row["previous_hash"], row["algorithm"])
                if recomputed != row["current_hash"]:
                    anomalies.append({
                        "type": "hash_mismatch", "seq": seq, "event_id": event_id,
                        "detail": "recomputed hash does not match recorded current_hash "
                                  "(events row may have been altered after signing)",
                    })

        prev_hash_expected = row["current_hash"]
        prev_seq = seq

    # 重複検出: events行はあるが対応するsignatureがない（署名漏れ/重複書き込み）
    unsigned = conn.execute(
        'SELECT event_id FROM events WHERE event_id NOT IN '
        '(SELECT event_id FROM event_signatures)'
    ).fetchall()
    for u in unsigned:
        anomalies.append({
            "type": "unsigned_event", "seq": None, "event_id": u["event_id"],
            "detail": "events row has no corresponding event_signatures entry",
        })

    # スキーマ整合性検証（Phase5-1.5 schema_auditへの委譲）
    # 注意: connが実際に開いているDBファイルを対象にする（テスト用tmp DB等で
    # 誤って本番DB_PATHを検証してしまうと長時間ロック待ちが発生するため）
    try:
        from schema_audit import audit_schema
        db_file_row = conn.execute("PRAGMA database_list").fetchone()
        db_file = db_file_row[2] if db_file_row else None  # columns: seq, name, file
        conn_db_path = Path(db_file) if db_file else DB_PATH
        schema_ok, schema_message = audit_schema(conn_db_path)
        if not schema_ok:
            anomalies.append({
                "type": "schema_inconsistency", "seq": None, "event_id": None,
                "detail": schema_message,
            })
    except Exception as e:
        anomalies.append({
            "type": "schema_audit_error", "seq": None, "event_id": None,
            "detail": str(e),
        })

    return {"ok": len(anomalies) == 0, "checked": checked, "anomalies": anomalies}


def diagnose(anomalies: list) -> list:
    """
    Recovery Support（STEP4）。異常を自動修復せず、診断結果と修復提案のみを返す。
    戻り値: [ {location, affected_range, candidate_cause, candidate_repair}, ... ]
    """
    causes = {
        "missing_seq": (
            "an event_signatures row was deleted, or events were signed out of order",
            "locate the missing event_id in the nearest pre-incident backup under data/, "
            "re-insert the events row if absent, then re-run sign_event for it and "
            "re-chain (re-sign) every subsequent seq forward",
        ),
        "chain_break": (
            "previous_hash was altered, or a row was inserted/removed without re-chaining",
            "compare with backup data/mocka_events_pre_*.db to find the diverging seq, "
            "then rebuild event_signatures from that seq forward via "
            "scripts/migrate_event_integrity.py",
        ),
        "hash_mismatch": (
            "the events row content changed after it was signed (possible direct DB edit "
            "bypassing the Gate)",
            "restore the affected event_id's row from the nearest backup, then re-sign "
            "it and every subsequent seq forward",
        ),
        "unsigned_event": (
            "an events row was inserted without going through sign_event "
            "(legacy data, or a write path that bypassed integrity.sign_event)",
            "run scripts/migrate_event_integrity.py to backfill signatures for "
            "unsigned rows in chronological order",
        ),
        "invalid_signature_version": (
            "signature_version on this row is not recognized by the running code "
            "(possible downgrade or corrupted write)",
            "confirm KNOWN_SIGNATURE_VERSIONS in phi_os/integrity.py covers this "
            "version; if it is genuinely invalid, re-sign the row",
        ),
        "invalid_algorithm": (
            "algorithm on this row is not registered in ALGORITHMS",
            "add the algorithm to phi_os/integrity.ALGORITHMS if it is a deliberate "
            "upgrade, otherwise treat as corruption and re-sign from backup",
        ),
        "missing_event_row": (
            "an event_signatures row exists with no matching events row "
            "(events row deleted after signing)",
            "restore the events row from backup using the event_id, "
            "then re-verify",
        ),
        "schema_inconsistency": (
            "events._source CHECK constraint no longer matches gate_policy.ALLOWED_SOURCE_VALUES",
            "run scripts/migrate_source_check.py and update gate_policy.py to match",
        ),
        "schema_audit_error": (
            "schema_audit could not run (DB or module access error)",
            "investigate the underlying error message directly",
        ),
    }

    report = []
    for a in anomalies:
        cause, repair = causes.get(
            a["type"], ("unclassified anomaly", "manual investigation required")
        )
        report.append({
            "location": {"seq": a.get("seq"), "event_id": a.get("event_id")},
            "affected_range": f"seq={a.get('seq')}" if a.get("seq") is not None else "n/a",
            "candidate_cause": cause,
            "candidate_repair": repair,
            "anomaly_type": a["type"],
            "anomaly_detail": a["detail"],
        })
    return report


def seal_baseline(git_commit: str, schema_version: str, gate_policy_version: str,
                   migration_version: str, test_summary: dict,
                   hash_algorithm: str = DEFAULT_ALGORITHM,
                   baseline_version: str = "1.0") -> dict:
    """
    STEP5 Baseline Seal。Hash Chain開始時点の基準点を記録する。
    呼び出し側（scripts/seal_baseline.py）がdata/integrity_baseline.jsonへの
    書き込みを担当し、本関数はレコード内容の構築のみを行う。
    """
    from datetime import datetime, timezone
    return {
        "baseline_version": baseline_version,
        "git_commit": git_commit,
        "schema_version": schema_version,
        "gate_policy_version": gate_policy_version,
        "signature_version": SIGNATURE_VERSION,
        "hash_algorithm": hash_algorithm,
        "migration_version": migration_version,
        "test_summary": test_summary,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


if __name__ == "__main__":
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        result = verify_chain(conn)
        print(f"{'OK' if result['ok'] else 'NG'}: checked={result['checked']} "
              f"anomalies={len(result['anomalies'])}")
        for a in result["anomalies"]:
            print(f"  - {a['type']} seq={a['seq']} event_id={a['event_id']}: {a['detail']}")
        sys.exit(0 if result["ok"] else 1)
    finally:
        conn.close()
