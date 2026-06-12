# phi_os/registry/taxonomy.py
"""
Registry層 — Event Taxonomy v1.1 への読み取り専用アクセス。

このモジュールはtaxonomy.json (FROZEN) への書き込みメソッドを
一切持たない。ise.taxonomy_validator の薄いラッパーとして提供する。
"""
from __future__ import annotations

from ise.taxonomy_validator import (
    load_taxonomy,
    is_valid_category,
    is_valid_event_type,
    validate_event_type,
    get_category,
    is_revision_update,
    VALID_CATEGORIES,
)


def get_taxonomy() -> dict:
    """taxonomy.jsonをロードし、FROZENであることを確認して返す。"""
    data = load_taxonomy()
    if data.get("status") != "FROZEN":
        raise RuntimeError("taxonomy.json is not FROZEN")
    return data


def is_valid_event(event_type: str) -> bool:
    return validate_event_type(event_type)


__all__ = [
    "get_taxonomy",
    "is_valid_event",
    "is_valid_category",
    "is_valid_event_type",
    "get_category",
    "is_revision_update",
    "VALID_CATEGORIES",
]
