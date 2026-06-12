# phios/core/orchestrator.py
"""Orchestrator — Interpreter -> Synthesizer -> Router -> Executor を束ねる"""
from __future__ import annotations

from phios.core.event_interpreter import InterpretedEvent
from phios.core.decision_synthesis import DecisionSynthesizer
from phios.core.semantic_router import SemanticRouter
from phios.core.executor import Executor


class Orchestrator:
    def __init__(self):
        self.synthesizer = DecisionSynthesizer()
        self.router = SemanticRouter()
        self.executor = Executor()

    def process(self, event_type: str, raw: dict | None = None) -> dict:
        raw = raw or {}
        event = InterpretedEvent(event_type, raw)
        action = self.synthesizer.synthesize(event)
        route_result = self.router.route(action)
        execution_result = self.executor.execute(route_result, action)

        return {
            "event_type": event.event_type,
            "meaning": event.meaning,
            "action": {
                "action_type": action.action_type,
                "target": action.target,
                "priority": action.priority,
                "reason": action.reason,
            },
            "route": route_result,
            "execution": execution_result,
        }
