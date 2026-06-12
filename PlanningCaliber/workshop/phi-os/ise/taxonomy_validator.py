# taxonomy_validator.py
"""Event Taxonomy v1.1 バリデータ

taxonomy.json (FROZEN, version 1.1) に定義されたカテゴリ・イベント名と
照合するための薄いユーティリティ。
"""
from __future__ import annotations

import json
from pathlib import Path

TAXONOMY_PATH = Path(__file__).resolve().parents[4] / "docs" / "mocka3" / "taxonomy.json"

VALID_CATEGORIES = {
    "state_transition",
    "state_operation",
    "audit",
    "lifecycle",
    "incident",
    "knowledge",
    "governance",
}


def load_taxonomy() -> dict:
    with open(TAXONOMY_PATH, encoding="utf-8") as f:
        return json.load(f)


def is_valid_category(category: str) -> bool:
    return category in VALID_CATEGORIES


def is_valid_event_type(category: str, event_type: str) -> bool:
    data = load_taxonomy()
    return event_type in data.get("events", {}).get(category, {})
