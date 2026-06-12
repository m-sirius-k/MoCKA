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


def validate_event_type(event_type: str) -> bool:
    """event_typeがTaxonomy v1.1のいずれかのカテゴリに定義されていればTrue"""
    data = load_taxonomy()
    events = data.get("events", {})
    return any(event_type in cat_events for cat_events in events.values())


def get_category(name: str) -> str | None:
    """
    nameがカテゴリ名そのものならそのカテゴリ名を返す。
    nameがevent_typeなら、それを含むカテゴリ名を返す。
    どちらにも該当しなければNone。
    """
    data = load_taxonomy()
    if name in data.get("categories", {}):
        return name
    events = data.get("events", {})
    for category, cat_events in events.items():
        if name in cat_events:
            return category
    return None


def is_revision_update(event_type: str) -> bool:
    """event_typeがrevisionを増加させる種別ならTrue（未定義はFalse）"""
    data = load_taxonomy()
    events = data.get("events", {})
    for cat_events in events.values():
        if event_type in cat_events:
            return bool(cat_events[event_type].get("revision_increment", False))
    return False


def get_severity(event_type: str) -> str:
    """event_typeのseverityを返す（未定義は"info"）"""
    category = get_category(event_type)
    if category is None:
        return "info"
    data = load_taxonomy()
    definition = data.get("events", {}).get(category, {}).get(event_type, {})
    return definition.get("severity", "info")
