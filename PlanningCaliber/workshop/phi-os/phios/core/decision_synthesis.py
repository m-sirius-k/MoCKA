# phios/core/decision_synthesis.py
"""DecisionSynthesis v1.1 — Decision Rulesを参照する"""
from __future__ import annotations

from phios.core.event_interpreter import InterpretedEvent
from phios.registry.decision_rules import match_rule


class Action:
    def __init__(self, action_type: str, target: str, priority: int, reason: str):
        self.action_type = action_type
        self.target = target
        self.priority = priority
        self.reason = reason


class DecisionSynthesizer:
    def synthesize(self, event: InterpretedEvent) -> Action:
        impact = event.meaning["impact"]
        intent = event.meaning["intent"]
        urgency = event.meaning["urgency"]

        rule = match_rule(impact, intent)

        return Action(
            action_type=rule.action_type,
            target=rule.target,
            priority=max(rule.priority_base, urgency),
            reason=f"{rule.action_type}:{event.event_type}",
        )
