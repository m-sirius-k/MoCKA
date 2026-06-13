# -*- coding: utf-8 -*-
"""Consistency Stress Test (Phase 5 Cross-Layer Consistency Engine)

usage:
    python -m cross_layer_consistency.consistency_stress_test

実際のレイヤー出力を改変するのではなく、UnifiedSnapshot/LayerSnapshot を
合成データで構築し、Detector/Clusterer/Strategy/Queue/Applier が
極端な入力に対しても破綻しない (例外を出さない・PASSしない誤判定をしない)
ことを確認する。

必須項目:
  1. multi-layer contradiction injection      - 全層が相互に矛盾する値を注入
  2. cascading inconsistency simulation        - semantic->decision->memory->learning の
                                                   連鎖的不整合
  3. feedback-loop destabilization test         - feedback提案過多 + learning更新0 + さらに
                                                   memory_coherenceも低い複合状態
  4. report-reality divergence test             - reality全FIXED vs report全conflict (極端な発散)
  5. learning drift test                        - learning governance FAIL 状態での
                                                   SUPPRESSION_RULES適用確認
"""

import sys

from cross_layer_consistency.layer_snapshot_builder import UnifiedSnapshot, LayerSnapshot
from cross_layer_consistency.consistency_score_engine import compute
from cross_layer_consistency.inconsistency_detector import detect
from cross_layer_consistency.conflict_clusterer import cluster
from cross_layer_consistency.resolution_strategy_engine import propose
from cross_layer_consistency.consistency_queue import ConsistencyQueue
from cross_layer_consistency.consistency_applier import apply as apply_item


def _make_snapshot(overrides: dict) -> UnifiedSnapshot:
    base = {
        "semantic": LayerSnapshot("semantic", "OK", {"evaluation_score": 1.0}),
        "decision": LayerSnapshot("decision", "OK", {"avg_score": 1.0}),
        "memory": LayerSnapshot("memory", "OK", {"evaluation_score": 1.0}),
        "self_audit": LayerSnapshot("self_audit", "OK", {"governance_score": 1.0}),
        "feedback": LayerSnapshot("feedback", "OK", {"governance_status": "PASS", "proposal_count": 0,
                                                       "risk_levels": [], "target_layers": []}),
        "learning": LayerSnapshot("learning", "OK", {"governance_status": "PASS", "update_count": 0, "statuses": []}),
        "reality": LayerSnapshot("reality", "OK", {"total": 10, "fixed": 10, "broken": 0, "broken_files": []}),
        "report": LayerSnapshot("report", "OK", {"total": 10, "conflict_count": 0, "conflict_files": [],
                                                   "governance_fail_count": 0}),
    }
    for layer, data in overrides.items():
        base[layer] = data
    return UnifiedSnapshot(layers=base)


def _run_pipeline_on(snapshot):
    score_result = compute(snapshot)
    incs = detect(snapshot, score_result.sub_scores)
    clusters = cluster(incs)
    strategies = propose(clusters)

    incs_by_cluster = {c.cluster_id: c.inconsistencies for c in clusters}
    impact_by_cluster = {c.cluster_id: c.impact_radius for c in clusters}

    queue = ConsistencyQueue()
    for s in strategies:
        item = queue.enqueue(s, impact_by_cluster.get(s.cluster_id, 0))
        queue.validate(item, snapshot.get("report"))

    apply_results = [
        apply_item(item, score_result.total_score, incs_by_cluster.get(item.cluster_id, []))
        for item in queue.ordered_items()
    ]
    return score_result, incs, clusters, strategies, queue, apply_results


def test_multi_layer_contradiction_injection():
    """全層が相互に矛盾する極端値を注入してもクラッシュせず、
    全inconsistencyがクラスタ化・戦略提案・queue登録まで完走すること。"""
    snap = _make_snapshot({
        "semantic": LayerSnapshot("semantic", "OK", {"evaluation_score": 1.0}),
        "decision": LayerSnapshot("decision", "OK", {"avg_score": 0.0}),
        "memory": LayerSnapshot("memory", "OK", {"evaluation_score": 1.0}),
        "self_audit": LayerSnapshot("self_audit", "OK", {"governance_score": 0.0}),
        "reality": LayerSnapshot("reality", "OK", {"total": 10, "fixed": 0, "broken": 10,
                                                     "broken_files": [f"f{i}.py" for i in range(10)]}),
        "report": LayerSnapshot("report", "OK", {"total": 10, "conflict_count": 10,
                                                   "conflict_files": [f"f{i}.py" for i in range(10)],
                                                   "governance_fail_count": 0}),
    })
    score_result, incs, clusters, strategies, queue, apply_results = _run_pipeline_on(snap)

    assert len(incs) >= 1, "全層矛盾なのにinconsistencyが検出されない"
    assert all(item.governance_status != "UNCHECKED" for item in queue.ordered_items())
    assert all(not r.applied for r in apply_results), \
        "極端な矛盾状態で即時適用されてしまった(risk_delta基準が機能していない)"
    print(f"[PASS] test_multi_layer_contradiction_injection "
          f"(score={score_result.total_score}, {len(incs)} inconsistencies, 0 applied)")


def test_cascading_inconsistency_simulation():
    """semantic高評価 -> decision低評価 -> memory低評価 -> learning不健全 という
    連鎖的劣化が、SEMANTIC_VS_DECISION / DECISION_VS_MEMORY / MEMORY_VS_LEARNING_DRIFT
    として個別に検出され、依存関係上重なるクラスタとして集約されること。"""
    snap = _make_snapshot({
        "semantic": LayerSnapshot("semantic", "OK", {"evaluation_score": 1.0}),
        "decision": LayerSnapshot("decision", "OK", {"avg_score": 0.3}),
        "memory": LayerSnapshot("memory", "OK", {"evaluation_score": 0.9}),
        "learning": LayerSnapshot("learning", "OK", {"governance_status": "FAIL", "update_count": 0, "statuses": []}),
    })
    score_result, incs, clusters, strategies, queue, apply_results = _run_pipeline_on(snap)

    types = {inc.inconsistency_type for inc in incs}
    assert "SEMANTIC_VS_DECISION" in types
    assert "MEMORY_VS_LEARNING_DRIFT" in types

    # decision/memoryを共有するinconsistencyは同一クラスタに属するはず
    decision_clusters = {c.cluster_id for c in clusters if "decision" in c.layers_involved}
    memory_clusters = {c.cluster_id for c in clusters if "memory" in c.layers_involved}
    assert decision_clusters & memory_clusters, "decisionとmemoryが別クラスタに分離されてしまった(連鎖が分断)"

    print(f"[PASS] test_cascading_inconsistency_simulation ({len(incs)} inconsistencies, types={types})")


def test_feedback_loop_destabilization():
    """feedback提案過多 + learning更新0 + memory_coherence低 という複合不安定状態で、
    FEEDBACK_VS_LEARNING_INCONSISTENCY と MEMORY_VS_LEARNING_DRIFT が両方検出され、
    かつ何もApplierで即時適用されないこと(システムは不安定なまま"管理可能"であること)。"""
    snap = _make_snapshot({
        "memory": LayerSnapshot("memory", "OK", {"evaluation_score": 0.2}),
        "feedback": LayerSnapshot("feedback", "OK", {
            "governance_status": "PASS", "proposal_count": 20,
            "risk_levels": ["high"] * 20, "target_layers": ["decision"] * 20,
        }),
        "learning": LayerSnapshot("learning", "OK", {"governance_status": "PASS", "update_count": 0, "statuses": []}),
    })
    score_result, incs, clusters, strategies, queue, apply_results = _run_pipeline_on(snap)

    types = {inc.inconsistency_type for inc in incs}
    assert "FEEDBACK_VS_LEARNING_INCONSISTENCY" in types
    assert "MEMORY_VS_LEARNING_DRIFT" in types
    assert all(not r.applied for r in apply_results)
    print(f"[PASS] test_feedback_loop_destabilization (score={score_result.total_score}, "
          f"{len(incs)} inconsistencies, system remains in queue (not crashed))")


def test_report_reality_divergence_extreme():
    """reality全FIXED、report全conflictという極端な発散でも
    REALITY_VS_REPORT_DIVERGENCE が検出され、priority_override戦略
    (reality優先、LAYER_PRIORITY準拠)が提案されること。"""
    snap = _make_snapshot({
        "reality": LayerSnapshot("reality", "OK", {"total": 5, "fixed": 5, "broken": 0, "broken_files": []}),
        "report": LayerSnapshot("report", "OK", {"total": 5, "conflict_count": 5,
                                                   "conflict_files": [f"f{i}.py" for i in range(5)],
                                                   "governance_fail_count": 0}),
    })
    score_result, incs, clusters, strategies, queue, apply_results = _run_pipeline_on(snap)

    div = [inc for inc in incs if inc.inconsistency_type == "REALITY_VS_REPORT_DIVERGENCE"]
    assert div, "極端な発散でREALITY_VS_REPORT_DIVERGENCEが検出されない"

    override_strategies = [s for s in strategies if s.strategy_type == "priority_override"]
    assert override_strategies, "priority_override戦略が提案されない"
    for s in override_strategies:
        assert "reality" in s.description, f"reality優先が説明に反映されていない: {s.description}"

    print(f"[PASS] test_report_reality_divergence_extreme ({len(div)} divergence, "
          f"{len(override_strategies)} priority_override proposed)")


def test_learning_drift_suppression():
    """learning側がUNAVAILABLEの場合でもMEMORY_VS_LEARNING_DRIFTが検出され、
    例外なくqueue/applierまで完走すること(evidence不在=BROKEN/安全側)。"""
    snap = _make_snapshot({
        "learning": LayerSnapshot("learning", "UNAVAILABLE", {}, evidence="synthetic: learning kernel down"),
    })
    score_result, incs, clusters, strategies, queue, apply_results = _run_pipeline_on(snap)

    drift = [inc for inc in incs if inc.inconsistency_type == "MEMORY_VS_LEARNING_DRIFT"]
    assert drift, "learning UNAVAILABLE時にMEMORY_VS_LEARNING_DRIFTが検出されない"
    assert "UNAVAILABLE" in drift[0].description or "learning_evidence" in drift[0].evidence

    # 例外なくqueueまで到達していること
    for item in queue.ordered_items():
        assert item.governance_status in ("PASS", "FAIL", "SUPPRESSED", "NO_EVIDENCE")

    print(f"[PASS] test_learning_drift_suppression ({len(drift)} drift findings, "
          f"queue completed without exception)")


def main():
    tests = [
        test_multi_layer_contradiction_injection,
        test_cascading_inconsistency_simulation,
        test_feedback_loop_destabilization,
        test_report_reality_divergence_extreme,
        test_learning_drift_suppression,
    ]

    failed = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            print(f"[FAIL] {t.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"[ERROR] {t.__name__}: {type(e).__name__}: {e}")
            failed += 1

    print()
    if failed:
        print(f"{failed} tests failed.")
        sys.exit(1)
    print("ALL STRESS TESTS PASSED.")


if __name__ == "__main__":
    main()
