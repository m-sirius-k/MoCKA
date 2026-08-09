# -*- coding: utf-8 -*-

"""Intent Parser

User request -> structured intent
"""


def parse_intent(request: str) -> dict:
    """
    Basic intent classification.

    This is the first layer of JARVIS Orchestrator.
    """

    text = request.lower()

    intent = "general"

    if "test" in text or "pytest" in text:
        intent = "verification"

    elif "fix" in text or "修正" in request:
        intent = "development"

    elif "調査" in request or "research" in text:
        intent = "research"

    return {
        "raw_request": request,
        "intent": intent,
    }