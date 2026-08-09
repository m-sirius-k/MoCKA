# -*- coding: utf-8 -*-

"""Agent Router

Task -> Agent assignment
"""


def route_task(task: str) -> dict:
    agent = "gpt"

    if "code" in task or "fix" in task:
        agent = "codex"

    elif "research" in task or "information" in task:
        agent = "gemini"

    elif "design" in task or "architecture" in task:
        agent = "claude"

    return {
        "task": task,
        "assigned_agent": agent,
    }