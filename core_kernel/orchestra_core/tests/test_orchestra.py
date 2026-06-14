"""
orchestra_core.tests.test_orchestra

Phase 12: Orchestra(意思決定層)設計のテスト。
"""

from core_kernel.orchestra_core import (
    DECISION_FIELD_AXES,
    EXECUTION_STATUS_PROPOSED,
    DecisionPacket,
    Orchestra,
    ProposalNode,
)


def _proposal(proposal_id, source="PHI-OS", confidence=0.5, cost=0.5, constraints=()):
    return ProposalNode(
        proposal_id=proposal_id,
        source=source,
        payload={"detail": proposal_id},
        confidence=confidence,
        cost=cost,
        constraints=constraints,
    )


# ----------------------------------------------------------------------
# ProposalNode / DecisionPacket データモデル
# ----------------------------------------------------------------------

def test_proposal_node_to_dict():
    proposal = _proposal("p1")
    d = proposal.to_dict()

    assert d["proposal_id"] == "p1"
    assert d["source"] == "PHI-OS"
    assert d["payload"] == {"detail": "p1"}
    assert d["constraints"] == []
    assert d["version"] == "1.0"


def test_decision_field_axes_fixed():
    assert DECISION_FIELD_AXES == (
        "structural_consistency",
        "temporal_stability",
        "resource_cost",
        "risk_containment",
        "future_compatibility",
    )


def test_decision_packet_execution_status_always_proposed():
    packet = DecisionPacket(selected_proposal={}, rejected_proposals=(), rationale="test")
    assert packet.execution_status == EXECUTION_STATUS_PROPOSED
    assert packet.to_dict()["execution_status"] == "PROPOSED"


# ----------------------------------------------------------------------
# Orchestra.evaluate / score
# ----------------------------------------------------------------------

def test_evaluate_returns_all_axes():
    orchestra = Orchestra()
    scores = orchestra.evaluate(_proposal("p1"))

    assert set(scores.keys()) == set(DECISION_FIELD_AXES)
    for value in scores.values():
        assert 0.0 <= value <= 1.0


def test_higher_confidence_lower_cost_scores_higher():
    orchestra = Orchestra()
    good = _proposal("good", confidence=0.9, cost=0.1)
    bad = _proposal("bad", confidence=0.1, cost=0.9)

    assert orchestra.score(good) > orchestra.score(bad)


# ----------------------------------------------------------------------
# Orchestra.decide
# ----------------------------------------------------------------------

def test_decide_with_no_proposals():
    orchestra = Orchestra()
    packet = orchestra.decide([])

    assert packet.selected_proposal is None
    assert packet.rejected_proposals == ()
    assert packet.execution_status == "PROPOSED"


def test_decide_selects_highest_scoring_proposal():
    orchestra = Orchestra()
    good = _proposal("good", confidence=0.9, cost=0.1)
    bad = _proposal("bad", confidence=0.1, cost=0.9)

    packet = orchestra.decide([bad, good])

    assert packet.selected_proposal["proposal_id"] == "good"
    assert len(packet.rejected_proposals) == 1
    assert packet.rejected_proposals[0]["proposal_id"] == "bad"
    assert packet.execution_status == "PROPOSED"


def test_decide_rationale_mentions_selected_proposal():
    orchestra = Orchestra()
    proposal = _proposal("only-one", confidence=0.8, cost=0.2)

    packet = orchestra.decide([proposal])

    assert "only-one" in packet.rationale
    assert packet.rejected_proposals == ()


def test_decide_with_constraints_reduces_score():
    orchestra = Orchestra()
    unconstrained = _proposal("free", confidence=0.7, cost=0.3, constraints=())
    constrained = _proposal("bound", confidence=0.7, cost=0.3, constraints=("c1", "c2", "c3"))

    assert orchestra.score(unconstrained) > orchestra.score(constrained)


# ----------------------------------------------------------------------
# 非侵襲性 / 実行禁止の確認
# ----------------------------------------------------------------------

def test_orchestra_has_no_external_state():
    """Orchestraはいずれの外部モジュールへの参照も保持しない。"""
    orchestra = Orchestra()
    assert vars(orchestra) == {}


def test_orchestra_module_does_not_reference_other_layers():
    """orchestra_coreはPHI-OS/Relay/Memory/PrismBridgeへの参照を一切持たない。"""
    import core_kernel.orchestra_core.orchestra as module

    with open(module.__file__, encoding="utf-8") as f:
        content = f.read()

    for forbidden in ("phios_integration", "relay_core", "memory_core", "PrismBridge"):
        assert f"import {forbidden}" not in content
        assert f"from .{forbidden}" not in content


def test_decision_packet_never_has_non_proposed_status():
    orchestra = Orchestra()
    packet = orchestra.decide([_proposal("p1"), _proposal("p2", confidence=0.9)])

    assert packet.to_dict()["execution_status"] == "PROPOSED"
