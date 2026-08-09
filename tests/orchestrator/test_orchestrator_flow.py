from orchestrator.agent_router import route_task
from orchestrator.context_injector import inject_context


def test_route_fix_code_to_codex():
    result = route_task("fix code")

    assert result["assigned_agent"] == "codex"


def test_context_injection_sources():
    result = inject_context("fix code")

    assert result["task"] == "fix code"
    assert "MOCKA_OVERVIEW" in result["context_sources"]
    assert "events_latest" in result["context_sources"]
    assert "decision_ledger" in result["context_sources"]


def test_router_context_integration():
    route = route_task("fix code")
    context = inject_context("fix code")

    assert route["task"] == context["task"]
    assert route["assigned_agent"] == "codex"