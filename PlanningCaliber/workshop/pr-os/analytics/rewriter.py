"""
PR-OS Analytics — AI Rewriter
GA4パフォーマンスデータを基にKSの改善提案を生成する
Phase 3: ルールベース提案（将来的にLLM連携可）
"""
import json
import os
import sys
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class RewriteSuggestion:
    ks_id:       str
    priority:    str          # "high" | "medium" | "low"
    category:    str          # "title" | "structure" | "length" | "seo" | "engagement"
    issue:       str
    suggestion:  str
    metric_basis: dict = field(default_factory=dict)


# ─────────────────────────────────────────
# Rule Engine
# ─────────────────────────────────────────
RULES = [
    {
        "id": "high_bounce",
        "condition": lambda m: m.get("bounce_rate", 0) > 0.7,
        "priority": "high",
        "category": "engagement",
        "issue": "直帰率が高い ({bounce_rate:.0%})",
        "suggestion": "冒頭3文で価値を明示する。見出し・箇条書きで可読性を上げる。内部リンクを追加する。"
    },
    {
        "id": "low_duration",
        "condition": lambda m: 0 < m.get("avg_duration", 99) < 30,
        "priority": "high",
        "category": "length",
        "issue": "平均滞在時間が短い ({avg_duration:.0f}秒)",
        "suggestion": "本文を充実させる（目安: 1,000文字以上）。動画・画像を追加して滞在を促す。"
    },
    {
        "id": "low_pageviews",
        "condition": lambda m: 0 < m.get("pageviews", 0) < 50,
        "priority": "medium",
        "category": "seo",
        "issue": "PVが少ない ({pageviews}PV)",
        "suggestion": "タイトルにキーワードを明示する。メタディスクリプションを最適化する。SNSシェアを促進する。"
    },
    {
        "id": "zero_new_users",
        "condition": lambda m: m.get("pageviews", 1) > 0 and m.get("new_users", 0) == 0,
        "priority": "medium",
        "category": "seo",
        "issue": "新規ユーザーが0人",
        "suggestion": "検索流入を増やすためのロングテールキーワードを追加する。外部SNSで拡散する。"
    },
    {
        "id": "good_performance",
        "condition": lambda m: (m.get("pageviews", 0) > 200
                                and m.get("bounce_rate", 1) < 0.4
                                and m.get("avg_duration", 0) > 120),
        "priority": "low",
        "category": "engagement",
        "issue": "高パフォーマンス記事",
        "suggestion": "関連記事・シリーズ展開を検討する。ニュースレターで再配信する価値あり。"
    },
]


def analyze(ks_id: str, metrics: dict) -> list[RewriteSuggestion]:
    """
    メトリクスに基づいて改善提案を生成。
    metrics: ga_connector.get_ks_performance() の戻り値
    """
    if metrics.get("mock"):
        return []

    suggestions = []
    for rule in RULES:
        try:
            if rule["condition"](metrics):
                issue = rule["issue"].format(**{
                    k: v for k, v in metrics.items()
                    if isinstance(v, (int, float))
                })
                suggestions.append(RewriteSuggestion(
                    ks_id=ks_id,
                    priority=rule["priority"],
                    category=rule["category"],
                    issue=issue,
                    suggestion=rule["suggestion"],
                    metric_basis={
                        "pageviews":    metrics.get("pageviews"),
                        "bounce_rate":  metrics.get("bounce_rate"),
                        "avg_duration": metrics.get("avg_duration"),
                        "new_users":    metrics.get("new_users"),
                    }
                ))
        except Exception:
            pass

    # 優先度順: high → medium → low
    order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda s: order.get(s.priority, 9))
    return suggestions


def analyze_all(days: int = 30) -> dict:
    """全確定済みKSの改善提案を一括生成"""
    from knowledge_store.ks_manager import list_records
    from analytics.ga_connector import get_ks_performance

    confirmed = list_records(status="confirmed")
    results = {}
    for rec in confirmed:
        metrics     = get_ks_performance(rec["id"], days=days)
        suggestions = analyze(rec["id"], metrics)
        results[rec["id"]] = {
            "title":       rec["title"],
            "metrics":     metrics,
            "suggestions": [s.__dict__ for s in suggestions]
        }
    return results


def report(days: int = 30) -> str:
    """テキストレポートを生成"""
    results = analyze_all(days)
    if not results:
        return "確定済みKSがありません。"

    lines = [f"# AI Rewriter Report — 過去{days}日間\n"]
    for ks_id, data in results.items():
        lines.append(f"## {ks_id}: {data['title']}")
        m = data["metrics"]
        if not m.get("mock"):
            lines.append(f"  PV:{m.get('pageviews',0):,} | "
                         f"直帰率:{m.get('bounce_rate',0):.0%} | "
                         f"滞在:{m.get('avg_duration',0):.0f}s")
        sug = data["suggestions"]
        if not sug:
            lines.append("  → 改善提案なし（GA未設定 or 問題なし）")
        else:
            for s in sug:
                icon = {"high":"🔴","medium":"🟡","low":"🟢"}.get(s["priority"],"·")
                lines.append(f"  {icon} [{s['category']}] {s['issue']}")
                lines.append(f"     → {s['suggestion']}")
        lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
