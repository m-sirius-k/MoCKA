# Phase9-2 smoke test - structure only, no algorithm.
#
# 確認するのはimportとインスタンス化、および候補生成が未実装である
# ことの明示(NotImplementedError)のみ。アルゴリズムのテストは
# Phase9-3以降。

import pytest

from semantic.query_engine.projection_candidate import EventCandidate, NLCandidate
from semantic.query_engine.projection_result import ProjectionResult, DIRECTION_NL_TO_EVENT
from semantic.query_engine.semantic_projection_layer import SemanticProjectionLayer


def test_event_candidate_construction():
    candidate = EventCandidate(cluster_id="c-1", canonical_trace_id="UV1", rationale="example")
    assert candidate.cluster_id == "c-1"


def test_nl_candidate_construction():
    candidate = NLCandidate(identifier="c-1", text="example text", source_field="why_this_meaning")
    assert candidate.text == "example text"


def test_projection_result_holds_sequence_only():
    result = ProjectionResult(direction=DIRECTION_NL_TO_EVENT, query="fix the bug", candidates=())
    assert isinstance(result.candidates, tuple)


def test_nl_to_event_candidates_not_yet_implemented():
    layer = SemanticProjectionLayer()
    with pytest.raises(NotImplementedError):
        layer.nl_to_event_candidates("fix the bug")


def test_event_to_nl_candidates_not_yet_implemented():
    layer = SemanticProjectionLayer()
    with pytest.raises(NotImplementedError):
        layer.event_to_nl_candidates("c-1")
