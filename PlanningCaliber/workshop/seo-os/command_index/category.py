"""command_index/category.py — CategoryManager"""
from __future__ import annotations
from .db import CommandIndexDB

_CATEGORIES = {
    "seo":          {"label": "SEO Engine",        "icon": "🔍", "order": 1},
    "publish":      {"label": "Publishing",         "icon": "📤", "order": 2},
    "distribution": {"label": "Distribution",       "icon": "🌐", "order": 3},
    "caliber":      {"label": "Caliber (AI)",       "icon": "🤖", "order": 4},
    "governance":   {"label": "Governance",         "icon": "🏛", "order": 5},
    "context":      {"label": "Context Runtime",    "icon": "🧠", "order": 6},
}


class CategoryManager:
    def __init__(self, db: CommandIndexDB | None = None) -> None:
        self._db = db or CommandIndexDB()

    def list_categories(self) -> list[dict]:
        rows = self._db.execute(
            "SELECT category, COUNT(*) as count FROM commands "
            "WHERE status='active' GROUP BY category ORDER BY category"
        )
        result = []
        for r in rows:
            cat = r["category"]
            meta = _CATEGORIES.get(cat, {"label": cat, "icon": "📁", "order": 99})
            result.append({
                "id": cat,
                "label": meta["label"],
                "icon": meta["icon"],
                "order": meta["order"],
                "count": r["count"],
            })
        return sorted(result, key=lambda x: x["order"])

    def get_label(self, category: str) -> str:
        return _CATEGORIES.get(category, {}).get("label", category)

    def get_commands_by_category(self, category: str) -> list[dict]:
        return self._db.execute(
            "SELECT id, name, description FROM commands "
            "WHERE category=? AND status='active' ORDER BY name",
            (category,)
        )
