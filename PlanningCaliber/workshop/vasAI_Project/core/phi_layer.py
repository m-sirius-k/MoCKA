"""
vasAI Core: PHI Layer — Decision DNA（判断の遺伝子）を保存する。
Evidence Ledgerが「記録→判断」なら、PHI Layerは「判断→継承」。
WHY → REASON → EVIDENCE → DECISION → OUTCOME
"""
import hashlib
import json
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

_lock = threading.Lock()
_conn_cache: dict[str, sqlite3.Connection] = {}


def _phi_db_path() -> Path:
    import os
    p = os.environ.get("VASAI_PHI_DB_PATH",
                       str(Path(__file__).parent.parent / "data" / "phi_layer.db"))
    return Path(p)


def _get_conn() -> sqlite3.Connection:
    path = str(_phi_db_path())
    with _lock:
        conn = _conn_cache.get(path)
        if conn is None:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(path, check_same_thread=False, isolation_level=None)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            _conn_cache[path] = conn
        return conn


def initialize() -> None:
    conn = _get_conn()
    with _lock:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS phi_dna (
                dna_id            TEXT PRIMARY KEY,
                decision_id       TEXT NOT NULL DEFAULT '',
                why               TEXT NOT NULL DEFAULT '',
                reason            TEXT NOT NULL DEFAULT '',
                evidence_ids      TEXT NOT NULL DEFAULT '[]',
                decision_summary  TEXT NOT NULL DEFAULT '',
                outcome           TEXT NOT NULL DEFAULT '',
                essence_exported  INTEGER NOT NULL DEFAULT 0,
                created_at        TEXT NOT NULL,
                outcome_at        TEXT NOT NULL DEFAULT '',
                prev_hash         TEXT NOT NULL DEFAULT 'GENESIS',
                hash              TEXT NOT NULL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS phi_seq (
                date_key TEXT PRIMARY KEY,
                counter  INTEGER NOT NULL DEFAULT 0
            )
        """)


def _next_id(conn: sqlite3.Connection) -> str:
    key = datetime.now(timezone.utc).strftime("%Y%m%d")
    row = conn.execute("SELECT counter FROM phi_seq WHERE date_key=?", (key,)).fetchone()
    n = (row["counter"] + 1) if row else 1
    conn.execute(
        "INSERT INTO phi_seq(date_key,counter) VALUES(?,?) "
        "ON CONFLICT(date_key) DO UPDATE SET counter=excluded.counter",
        (key, n),
    )
    return f"PHI{key}_{n:06d}"


def _hash_fields(fields: list) -> str:
    parts = [str(f) if f is not None else "" for f in fields]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def _latest_hash(conn: sqlite3.Connection) -> str:
    row = conn.execute(
        "SELECT hash FROM phi_dna ORDER BY dna_id DESC LIMIT 1"
    ).fetchone()
    return row["hash"] if row else "GENESIS"


class PHILayer:
    """
    Decision DNAを管理するPHI Layer。
    vasAI の判断哲学をMoCKAへ還流する統合点。
    """

    def record_dna(
        self,
        decision_id: str,
        why: str,
        reason: str,
        evidence_ids: list[str],
        decision_summary: str,
    ) -> str:
        """Decision DNAを記録してdna_idを返す。"""
        initialize()
        created_at = datetime.now(timezone.utc).isoformat()
        ev_ids_str = json.dumps(evidence_ids, ensure_ascii=False)

        conn = _get_conn()
        with _lock:
            conn.execute("BEGIN IMMEDIATE")
            try:
                dna_id = _next_id(conn)
                prev_hash = _latest_hash(conn)
                h = _hash_fields([
                    dna_id, decision_id, why, reason,
                    ev_ids_str, decision_summary, created_at, prev_hash,
                ])
                conn.execute(
                    "INSERT INTO phi_dna VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                    (dna_id, decision_id, why, reason, ev_ids_str,
                     decision_summary, "", 0, created_at, "", prev_hash, h),
                )
                conn.execute("COMMIT")
            except Exception:
                conn.execute("ROLLBACK")
                raise
        return dna_id

    def record_outcome(self, dna_id: str, outcome: str) -> None:
        """事後結果を記録（Outcomeは後から追記）。"""
        initialize()
        outcome_at = datetime.now(timezone.utc).isoformat()
        conn = _get_conn()
        conn.execute(
            "UPDATE phi_dna SET outcome=?, outcome_at=? WHERE dna_id=?",
            (outcome, outcome_at, dna_id),
        )

    def get_full_dna(self, decision_id: str) -> dict:
        """WHY→REASON→EVIDENCE→DECISION→OUTCOME の全チェーン。"""
        initialize()
        conn = _get_conn()
        rows = conn.execute(
            "SELECT * FROM phi_dna WHERE decision_id=? ORDER BY dna_id ASC",
            (decision_id,),
        ).fetchall()

        if not rows:
            return {"decision_id": decision_id, "found": False, "dna": []}

        dna_list = []
        for row in rows:
            d = dict(row)
            d["evidence_ids"] = json.loads(d["evidence_ids"])
            d["has_outcome"] = bool(d["outcome"])
            dna_list.append(d)

        return {
            "decision_id":   decision_id,
            "found":         True,
            "dna_count":     len(dna_list),
            "dna":           dna_list,
            "chain_stages":  ["WHY", "REASON", "EVIDENCE", "DECISION", "OUTCOME"],
            "all_stages_complete": all(
                bool(d["why"]) and bool(d["reason"]) and
                bool(d["decision_summary"]) and bool(d["outcome"])
                for d in dna_list
            ),
        }

    def export_to_essence(self, dna_id: str) -> dict:
        """MoCKA essence形式にエクスポート（PHILOSOPHY/OPERATION軸）。"""
        initialize()
        conn = _get_conn()
        row = conn.execute(
            "SELECT * FROM phi_dna WHERE dna_id=?", (dna_id,)
        ).fetchone()
        if row is None:
            return {"error": f"DNA not found: {dna_id}"}

        d = dict(row)
        d["evidence_ids"] = json.loads(d["evidence_ids"])

        essence = {
            "dna_id":     dna_id,
            "source":     "vasAI",
            "PHILOSOPHY": {
                "why":    d["why"],
                "reason": d["reason"],
            },
            "OPERATION": {
                "decision": d["decision_summary"],
                "outcome":  d["outcome"],
                "evidence_count": len(d["evidence_ids"]),
            },
            "INCIDENT": {
                "is_failure": bool(d["outcome"]) and "失敗" in d["outcome"],
                "failure_detail": d["outcome"] if "失敗" in d.get("outcome", "") else "",
            },
            "exported_at": datetime.now(timezone.utc).isoformat(),
        }

        conn.execute(
            "UPDATE phi_dna SET essence_exported=1 WHERE dna_id=?", (dna_id,)
        )
        return essence

    def explain_decision(self, decision_id: str) -> str:
        """自然言語で「なぜこの判断をしたか」を説明する。"""
        full = self.get_full_dna(decision_id)
        if not full["found"] or not full["dna"]:
            return f"decision_id={decision_id} に対するDNAが見つかりません。"

        parts = [f"【判断DNA: decision_id={decision_id}】"]
        for dna in full["dna"]:
            parts += [
                f"  [背景・文脈] {dna['why']}",
                f"  [推論プロセス] {dna['reason']}",
                f"  [判断] {dna['decision_summary']}",
                f"  [根拠] Evidence Ledger参照 ({len(dna['evidence_ids'])}件)",
            ]
            if dna["outcome"]:
                parts.append(f"  [結果] {dna['outcome']}")
            else:
                parts.append(f"  [結果] 未記録（事後追記予定）")
        return "\n".join(parts)

    def verify_chain(self) -> bool:
        """全PHI DNAのhashチェーン検証。"""
        initialize()
        conn = _get_conn()
        rows = conn.execute(
            "SELECT * FROM phi_dna ORDER BY dna_id ASC"
        ).fetchall()
        if not rows:
            return True
        prev = "GENESIS"
        for row in rows:
            d = dict(row)
            if d["prev_hash"] != prev:
                return False
            expected = _hash_fields([
                d["dna_id"], d["decision_id"], d["why"], d["reason"],
                d["evidence_ids"], d["decision_summary"], d["created_at"], d["prev_hash"],
            ])
            if expected != d["hash"]:
                return False
            prev = d["hash"]
        return True

    def get_stats(self) -> dict:
        initialize()
        conn = _get_conn()
        total = conn.execute("SELECT COUNT(*) as c FROM phi_dna").fetchone()["c"]
        with_outcome = conn.execute(
            "SELECT COUNT(*) as c FROM phi_dna WHERE outcome != ''"
        ).fetchone()["c"]
        exported = conn.execute(
            "SELECT COUNT(*) as c FROM phi_dna WHERE essence_exported=1"
        ).fetchone()["c"]
        return {
            "total_dna":     total,
            "with_outcome":  with_outcome,
            "exported":      exported,
            "outcome_rate":  round(with_outcome / total * 100, 1) if total > 0 else 0,
        }
