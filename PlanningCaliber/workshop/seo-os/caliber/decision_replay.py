import json, sqlite3, os
from datetime import datetime
from kernel.logger import info, warn

DB_PATH = os.path.join(os.path.dirname(__file__),
                       "../data/jobs.db")

class DecisionReplayer:
    """
    Decision Ledgerに記録された過去の判断を再現する。
    当時のWorker候補・Strategy・スコアを復元して表示する。
    監査・デバッグ・説明責任のために使用。
    """

    def replay(self, decision_id: str) -> dict:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        row  = conn.execute("""
            SELECT * FROM decision_ledger WHERE id=?
        """, (decision_id,)).fetchone()
        conn.close()

        if not row:
            return {"error": f"Decision {decision_id} 未発見"}

        d = dict(row)
        try:
            candidates = json.loads(
                d.get("candidate_workers","[]"))
        except Exception:
            candidates = []
        try:
            reason = json.loads(
                d.get("selection_reason","{}"))
        except Exception:
            reason = {}

        replay_steps = []
        for c in candidates:
            name     = c if isinstance(c,str) else c
            is_selected = (name == d["selected_worker"])
            score_info = {}
            if isinstance(reason.get("candidates"), list):
                for rc in reason["candidates"]:
                    if rc.get("name") == name:
                        score_info = rc
                        break
            replay_steps.append({
                "worker":      name,
                "selected":    is_selected,
                "priority":    score_info.get("priority","?"),
                "success_rate":score_info.get("success_rate","?"),
                "avg_ms":      score_info.get("avg_ms","?"),
                "state":       score_info.get("state","?")
            })

        explanation = self._build_text(d, replay_steps)

        return {
            "decision_id":    decision_id,
            "timestamp":      d["timestamp"],
            "capability":     d["capability"],
            "strategy":       d["strategy"],
            "selected_worker":d["selected_worker"],
            "outcome":        d.get("outcome",""),
            "job_id":         d.get("job_id",""),
            "candidates":     replay_steps,
            "explanation":    explanation
        }

    def replay_by_job(self, job_id: str) -> list:
        """Job単位で全Decisionをreplay"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("""
            SELECT id FROM decision_ledger
            WHERE job_id=?
            ORDER BY timestamp
        """, (job_id,)).fetchall()
        conn.close()
        return [self.replay(r["id"]) for r in rows]

    def _build_text(self, d: dict,
                    candidates: list) -> str:
        lines = [
            f"=== Decision Replay ===",
            f"ID:         {d['id']}",
            f"Timestamp:  {d['timestamp']}",
            f"Capability: {d['capability']}",
            f"Strategy:   {d['strategy']}",
            f"Selected:   {d['selected_worker']}",
            f"Outcome:    {d.get('outcome','未確定')}",
            f"",
            f"当時の候補:"
        ]
        for c in candidates:
            mark = "→ [選択]" if c["selected"] else "  "
            lines.append(
                f"  {mark} {c['worker']}: "
                f"priority={c['priority']} "
                f"success={c['success_rate']}% "
                f"avg={c['avg_ms']}ms "
                f"state={c['state']}")
        return "\n".join(lines)
