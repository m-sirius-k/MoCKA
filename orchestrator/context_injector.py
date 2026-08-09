# -*- coding: utf-8 -*-

"""Context Injector

Provide required context for agents.
"""


def inject_context(task: str) -> dict:
    return {
        "task": task,
        "context_sources": [
            "MOCKA_OVERVIEW",
            "events_latest",
            "decision_ledger",
        ],
    }