import sqlite3, uuid, json, os
from datetime import datetime
from kernel.logger import info

DB_PATH = os.path.join(os.path.dirname(__file__),
                       "../data/jobs.db")

class DecisionLedger:
    """
    なぜそのWorkerが選ばれたかを記録する台帳。
    Performance Ledgerが「何が起きたか」なら
    Decision Ledgerは「なぜそうなったか」。
    MoCKA設計思想: 判断根拠を必ず残す。
    """

    def record(self, capability: str, strategy: str,
               selected: object, candidates: list,
               reason: dict, job_id: str = "",
               operator: str = "system") -> str:
        did = str(uuid.uuid4())
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            INSERT INTO decision_ledger
            (id,timestamp,capability,strategy,
             selected_worker,candidate_workers,
             selection_reason,job_id,operator)
            VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            did,
            datetime.now().isoformat(),
            capability,
            strategy,
            selected.name if selected else "none",
            json.dumps([c.name for c in candidates],
                       ensure_ascii=False),
            json.dumps(reason, ensure_ascii=False),
            job_id,
            operator
        ))
        conn.commit()
        conn.close()
        info(f"[Decision] 記録: {capability} "
             f"→ {selected.name if selected else 'none'} "
             f"/ strategy={strategy}")
        return did

    def update_outcome(self, decision_id: str,
                       outcome: str) -> None:
        """Job完了後にoutcomeを更新（done/failed）"""
        conn = sqlite3.connect(DB_PATH)
        conn.execute("""
            UPDATE decision_ledger
            SET outcome=? WHERE id=?
        """, (outcome, decision_id))
        conn.commit()
        conn.close()

    def get_by_capability(self, capability: str,
                          limit: int = 20) -> list:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT * FROM decision_ledger
            WHERE capability=?
            ORDER BY timestamp DESC LIMIT ?
        """, (capability, limit)).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def all(self, limit: int = 50) -> list:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT * FROM decision_ledger
            ORDER BY timestamp DESC LIMIT ?
        """, (limit,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]
