# phios/registry/meaning.py
"""Meaning Registry — 意味定義の固定層（読み取り専用）"""
from __future__ import annotations

# intent定義: categoryからintentへのマッピング
CATEGORY_INTENT_MAP: dict[str, str] = {
    "state_transition": "transition",
    "state_operation":  "observe",
    "audit":            "validate",
    "lifecycle":        "observe",
    "incident":         "recover",
    "knowledge":        "observe",
    "governance":       "govern",
}

# 個別上書き（event_typeレベル）
EVENT_INTENT_OVERRIDES: dict[str, str] = {
    "VIOLATION":        "recover",
    "AUTHORITY_REVOKE": "govern",
    "STATE_DEGRADED":   "recover",
    "SEAL":             "validate",
    "VERIFY":           "validate",
    "VERIFY_CHAIN":     "validate",
}

# impact定義: event_typeからimpactへのマッピング
SYSTEM_IMPACT_EVENTS: set[str] = {
    "STATE_CHANGE", "STATE_DEGRADED", "STATE_RECOVERED",
    "SNAPSHOT_LOAD", "REVISION_UPDATE", "STATE_SUSPENDED",
}

# urgency定義: severityからurgencyへのマッピング
SEVERITY_URGENCY_MAP: dict[str, int] = {
    "info":     1,
    "warning":  2,
    "critical": 3,
}


def get_intent(event_type: str, category: str | None) -> str:
    return EVENT_INTENT_OVERRIDES.get(
        event_type,
        CATEGORY_INTENT_MAP.get(category, "observe")
    )


def get_impact(event_type: str, severity: str) -> str:
    if severity == "critical":
        return "critical"
    if event_type in SYSTEM_IMPACT_EVENTS:
        return "system"
    return "local"


def get_urgency(severity: str) -> int:
    return SEVERITY_URGENCY_MAP.get(severity, 1)
