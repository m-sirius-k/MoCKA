# -*- coding: utf-8 -*-

"""Task Planner

Intent -> executable task list
"""


def plan_tasks(intent_data: dict) -> dict:
    intent = intent_data.get("intent", "general")

    tasks = []

    if intent == "verification":
        tasks = [
            "run_tests",
            "collect_results",
            "analyze_failures",
        ]

    elif intent == "development":
        tasks = [
            "inspect_code",
            "prepare_fix",
            "verify_change",
        ]

    elif intent == "research":
        tasks = [
            "collect_information",
            "summarize_findings",
        ]

    else:
        tasks = [
            "clarify_request",
        ]

    return {
        "intent": intent,
        "tasks": tasks,
    }
