"""
MoCKA 3.0 — GL1~GL7 統合テスト

各Governance Layerが単独で動作するだけでなく、
GL1 -> GL2 -> GL3 -> GL6 -> GL7 -> GL4/GL5 という連鎖で
一貫して動作することを確認する。
"""

from grounding_engine import RepositoryGroundingEngine
from working_memory import WorkingMemoryEngine
from thinking_mode import ThinkingModeEngine, ThinkingMode
from reasoning_governance import ReasoningGovernanceEngine
from execution_governance import ExecutionGovernanceEngine
from knowledge_mass import KnowledgeMassEngine
from consensus import ConsensusEngine


def check(label, condition):
    status = "OK" if condition else "FAIL"
    print(f"[{status}] {label}")
    return condition


def main():
    results = []

    # GL1: Grounding
    grounding_engine = RepositoryGroundingEngine()
    grounding = grounding_engine.ground("integration_test")
    results.append(check("GL1 grounding has repository_root", bool(grounding.repository_root)))
    results.append(check("GL1 grounding has current_branch", bool(grounding.current_branch)))

    # GL2: Working Memory bootstraps from GL1
    wm = WorkingMemoryEngine()
    memory = wm.load()
    results.append(check(
        "GL2 working memory bootstrapped from GL1 (repository matches)",
        memory["current_repository"] == grounding.repository_root,
    ))

    # GL3: Thinking Mode detection + explicit transition via GL2
    tm = ThinkingModeEngine()
    detected = tm.detect_mode("GL1-7 integration test, audit run")
    results.append(check("GL3 detect_mode returns AUDIT for audit task", detected == ThinkingMode.AUDIT))
    tm.set_mode(ThinkingMode.AUDIT, event="integration_test_set_mode")
    current = tm.get_current_mode()
    results.append(check("GL3 set_mode persisted via GL2", current == ThinkingMode.AUDIT))
    results.append(check(
        "GL3 forbids write_code while in AUDIT mode",
        tm.validate_action_for_mode("write_code", current) is False,
    ))

    # GL6: Reasoning Governance reads GL1/GL2/GL3
    reasoning = ReasoningGovernanceEngine()
    seq_ok = reasoning.validate_reasoning_sequence(
        ["task_receive", "working_memory", "repository_grounding", "current_thinking_mode"]
    )
    results.append(check("GL6 reasoning sequence valid (in-order subset)", seq_ok.ok))

    wm.update("integration_test_set_event", {"current_event": "E_integration_test"})
    checklist = reasoning.enforce_pre_answer_checklist()
    results.append(check(
        "GL6 pre-answer checklist passes once GL2/GL3 populated",
        checklist.ok,
    ))

    # GL7: Execution Governance dry run / abort detection
    execution = ExecutionGovernanceEngine()
    approval_unscoped = execution.pre_execution_check({"scope": ["structural", "data"]})
    results.append(check(
        "GL7 dry run produces a result with change_count",
        approval_unscoped.dry_run.change_count >= 0,
    ))

    approval_full_scope = execution.pre_execution_check({"scope": [
        p.name for p in __import__("pathlib").Path(r"C:\Users\sirok\MoCKA").iterdir()
    ]})
    results.append(check(
        "GL7 approves when scope covers all changed top-level dirs",
        approval_full_scope.dry_run.aborts == [] or approval_full_scope.approved,
    ))

    # GL4: Knowledge Mass uses GL3 context (AUDIT mode set above)
    km = KnowledgeMassEngine()
    candidates = [
        {"id": "rules",  "category": "repository_rules", "match": 0.5},
        {"id": "memo",   "category": "temporary_memo",   "match": 0.99},
    ]
    ranked = km.rank(candidates)
    results.append(check(
        "GL4 ranks repository_rules above temporary_memo under AUDIT context",
        ranked[0].candidate["id"] == "rules",
    ))
    status = km.status()
    results.append(check(
        "GL4 status reflects GL3 AUDIT mode",
        status["current_thinking_mode"] == "audit",
    ))

    # GL5: Consensus, status reflects GL1-3/6
    cs = ConsensusEngine()
    consensus_result = cs.run([
        {"claude": "X", "gpt": "X", "gemini": "X"},
    ])
    results.append(check("GL5 converges on unanimous round 1", consensus_result.converged))
    cs_status = cs.status()
    results.append(check(
        "GL5 status reflects GL1 repository_root",
        cs_status["repository_root"] == grounding.repository_root,
    ))

    print()
    total, passed = len(results), sum(results)
    print(f"{passed}/{total} checks passed")
    if passed != total:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
