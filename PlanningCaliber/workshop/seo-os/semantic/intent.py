"""semantic/intent.py — IntentResolver: クエリ→意図カテゴリ判定"""
from __future__ import annotations
import re

_INTENT_PATTERNS = [
    ("publish",     [r"publish", r"deploy", r"release", r"post", r"send", r"distribute"]),
    ("seo",         [r"seo", r"keyword", r"meta", r"ogp", r"schema", r"sitemap", r"robots",
                     r"canonical", r"readability", r"rank", r"optimize"]),
    ("analyze",     [r"analyz", r"check", r"verify", r"validate", r"audit", r"inspect"]),
    ("save",        [r"save", r"backup", r"snapshot", r"archive", r"checkpoint", r"store"]),
    ("search",      [r"find", r"search", r"look", r"query", r"where", r"list"]),
    ("execute",     [r"run", r"execute", r"start", r"launch", r"perform"]),
    ("context",     [r"context", r"memory", r"state", r"resume", r"restore", r"history"]),
    ("distribute",  [r"wordpress", r"sftp", r"twitter", r"instagram", r"x\.com", r"social"]),
    ("caliber",     [r"caliber", r"worker", r"health", r"recommend", r"lifecycle"]),
]


class IntentResolver:
    def resolve(self, query: str) -> str:
        q = query.lower()
        scores: dict[str, int] = {}
        for intent, patterns in _INTENT_PATTERNS:
            score = sum(1 for p in patterns if re.search(p, q))
            if score:
                scores[intent] = score
        if not scores:
            return "general"
        return max(scores, key=lambda k: scores[k])

    def resolve_all(self, query: str) -> list[tuple[str, int]]:
        q = query.lower()
        scores: dict[str, int] = {}
        for intent, patterns in _INTENT_PATTERNS:
            score = sum(1 for p in patterns if re.search(p, q))
            if score:
                scores[intent] = score
        return sorted(scores.items(), key=lambda x: -x[1])

    def intent_to_category(self, intent: str) -> str | None:
        mapping = {
            "publish":    "publish",
            "seo":        "seo",
            "analyze":    "seo",
            "save":       "governance",
            "search":     None,
            "execute":    "publish",
            "context":    "context",
            "distribute": "distribution",
            "caliber":    "caliber",
        }
        return mapping.get(intent)
