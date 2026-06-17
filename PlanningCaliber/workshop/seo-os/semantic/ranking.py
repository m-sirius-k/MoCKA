"""semantic/ranking.py — SimilarityRanking: 使用頻度・成功率を加味したランキング"""
from __future__ import annotations
from .search import SearchResult, MeaningSearch
from command_index.db import CommandIndexDB


class SimilarityRanking:
    def __init__(self, db: CommandIndexDB | None = None) -> None:
        self._db = db or CommandIndexDB()
        self._search = MeaningSearch(self._db)

    def rank(self, query: str, limit: int = 10,
             category: str | None = None,
             boost_recent: bool = True) -> list[SearchResult]:
        results = self._search.search(query, limit=limit * 2, category=category)
        if not results:
            return []

        # 使用ログからブースト係数を計算
        usage = self._get_usage_stats()

        for r in results:
            uid = r.command.id
            stats = usage.get(uid, {"use_count": 0, "success_rate": 1.0, "recency": 0})
            # 使用頻度ブースト (対数スケール)
            freq_boost = min(0.3, (stats["use_count"] ** 0.5) * 0.05)
            # 成功率ブースト
            success_boost = (stats["success_rate"] - 0.5) * 0.2
            # 最近使用ブースト
            recency_boost = stats["recency"] * 0.1 if boost_recent else 0
            r.score = min(1.0, r.score + freq_boost + success_boost + recency_boost)

        results.sort(key=lambda x: -x.score)
        return results[:limit]

    def top_commands(self, limit: int = 10) -> list[dict]:
        return self._db.execute(
            "SELECT command_id, COUNT(*) as use_count, "
            "SUM(CASE WHEN result='success' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as success_rate, "
            "MAX(logged_at) as last_used "
            "FROM usage_log GROUP BY command_id "
            "ORDER BY use_count DESC LIMIT ?",
            (limit,)
        )

    def _get_usage_stats(self) -> dict[str, dict]:
        rows = self._db.execute(
            "SELECT command_id, COUNT(*) as use_count, "
            "SUM(CASE WHEN result='success' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) as success_rate, "
            "MAX(logged_at) as last_used "
            "FROM usage_log GROUP BY command_id"
        )
        result = {}
        all_counts = [r["use_count"] for r in rows] or [1]
        max_count = max(all_counts)
        for r in rows:
            result[r["command_id"]] = {
                "use_count": r["use_count"],
                "success_rate": r["success_rate"] or 1.0,
                "recency": r["use_count"] / max_count,
            }
        return result
