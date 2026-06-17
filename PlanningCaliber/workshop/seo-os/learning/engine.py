"""learning/engine.py — LearningEngine: 使用頻度・成功率・傾向を記録しランキングへ反映"""
from __future__ import annotations
from datetime import datetime, timezone
from command_index.db import CommandIndexDB


class LearningEngine:
    def __init__(self, db: CommandIndexDB | None = None) -> None:
        self._db = db or CommandIndexDB()

    def record(self, command_id: str, result: str = "success",
               context: str = "") -> None:
        now = datetime.now(timezone.utc).isoformat()
        self._db.execute_write(
            "INSERT INTO usage_log(command_id,result,context,logged_at) VALUES(?,?,?,?)",
            (command_id, result, context, now)
        )

    def stats(self, command_id: str) -> dict:
        rows = self._db.execute(
            "SELECT COUNT(*) as total, "
            "SUM(CASE WHEN result='success' THEN 1 ELSE 0 END) as successes, "
            "MAX(logged_at) as last_used "
            "FROM usage_log WHERE command_id=?", (command_id,)
        )
        r = rows[0] if rows else {}
        total = r.get("total") or 0
        successes = r.get("successes") or 0
        return {
            "command_id": command_id,
            "use_count": total,
            "success_count": successes,
            "failure_count": total - successes,
            "success_rate": round(successes / total, 3) if total > 0 else 1.0,
            "last_used": r.get("last_used"),
        }

    def user_tendency(self, limit: int = 10) -> list[dict]:
        return self._db.execute(
            "SELECT command_id, COUNT(*) as use_count, "
            "SUM(CASE WHEN result='success' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as success_rate, "
            "MAX(logged_at) as last_used "
            "FROM usage_log GROUP BY command_id "
            "ORDER BY use_count DESC LIMIT ?", (limit,)
        )

    def recent(self, limit: int = 10) -> list[dict]:
        return self._db.execute(
            "SELECT command_id, result, logged_at FROM usage_log "
            "ORDER BY logged_at DESC LIMIT ?", (limit,)
        )

    def failure_analysis(self) -> list[dict]:
        return self._db.execute(
            "SELECT command_id, COUNT(*) as fail_count FROM usage_log "
            "WHERE result='failure' GROUP BY command_id "
            "ORDER BY fail_count DESC LIMIT 10"
        )

    def ranking(self, limit: int = 10) -> list[dict]:
        """使用頻度・成功率・最近使用を統合したランキング"""
        rows = self._db.execute(
            "SELECT command_id, COUNT(*) as use_count, "
            "SUM(CASE WHEN result='success' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as success_rate, "
            "MAX(logged_at) as last_used "
            "FROM usage_log GROUP BY command_id"
        )
        if not rows:
            return []
        max_count = max(r["use_count"] for r in rows) or 1
        scored = []
        for r in rows:
            freq = r["use_count"] / max_count
            sr = r["success_rate"] or 1.0
            score = freq * 0.5 + sr * 0.5
            scored.append({
                "command_id": r["command_id"],
                "use_count": r["use_count"],
                "success_rate": round(sr, 3),
                "last_used": r["last_used"],
                "score": round(score, 3),
            })
        return sorted(scored, key=lambda x: -x["score"])[:limit]
