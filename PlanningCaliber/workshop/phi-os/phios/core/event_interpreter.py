# phios/core/event_interpreter.py
"""EventInterpreter v1.1 — Meaning Registryを参照する"""
from __future__ import annotations

from phios.registry.taxonomy import get_category, get_severity
from phios.registry.meaning import get_intent, get_impact, get_urgency


class InterpretedEvent:
    def __init__(self, event_type: str, raw: dict):
        self.event_type = event_type
        self.category = get_category(event_type)
        self.severity = get_severity(event_type)
        self.raw = raw
        self.meaning = self._interpret()

    def _interpret(self) -> dict:
        return {
            "intent": get_intent(self.event_type, self.category),
            "impact": get_impact(self.event_type, self.severity),
            "urgency": get_urgency(self.severity),
        }
