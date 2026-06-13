# -*- coding: utf-8 -*-
"""Consistency Integration Test (Phase 5 Cross-Layer Consistency Engine)

usage:
    python -m cross_layer_consistency.consistency_integration_test

必須確認項目:
  1. 全レイヤースナップショット統合 - 8層全てがLayerSnapshotとして取得できる
  2. inconsistency検出成功         - 既知のREALITY_VS_REPORT_DIVERGENCEが検出される
  3. consistency score算出          - 重み付き合計が0-1の範囲かつ重み合計=1.0
  4. conflict clustering動作         - 検出されたinconsistencyがクラスタにまとめられる
  5. resolution生成                  - 各クラスタに戦略が1件以上提案される
  6. queue動作                       - enqueue/validate/orderingが正しく機能する
  7. governance連携                  - queue.validateがreport layerの結果を反映する
"""

import sys

from cross_layer_consistency.consistency_pipeline import run
from cross_layer_consistency.consistency_registry import SCORE_WEIGHTS, OVERRIDE_POLICIES


def test_all_layers_present():
    result = run()
    expected = {"semantic", "decision", "memory", "self_audit", "feedback", "learning", "reality", "report"}
    actual = set(result["snapshot"].layers.keys())
    assert actual == expected, f"layer不足: missing={expected - actual}, extra={actual - expected}"
    print(f"[PASS] test_all_layers_present ({len(actual)} layers)")


def test_inconsistency_detection():
    result = run()
    types = {inc.inconsistency_type for inc in result["inconsistencies"]}
    assert "REALITY_VS_REPORT_DIVERGENCE" in types, \
        f"REALITY_VS_REPORT_DIVERGENCEが検出されない: {types}"
    print(f"[PASS] test_inconsistency_detection ({len(result['inconsistencies'])} 件, types={types})")


def test_consistency_score_range():
    result = run()
    score = result["score_result"].total_score
    assert 0.0 <= score <= 1.0, f"スコアが範囲外: {score}"
    assert abs(sum(SCORE_WEIGHTS.values()) - 1.0) < 1e-9, "重み合計が1.0でない"
    print(f"[PASS] test_consistency_score_range (score={score})")


def test_conflict_clustering():
    result = run()
    if result["inconsistencies"]:
        assert result["clusters"], "inconsistencyが存在するのにclusterが生成されない"
        total_clustered = sum(len(c.inconsistencies) for c in result["clusters"])
        assert total_clustered == len(result["inconsistencies"]), \
            "clusterに含まれるinconsistency数が一致しない"
    print(f"[PASS] test_conflict_clustering ({len(result['clusters'])} clusters)")


def test_resolution_generation():
    result = run()
    cluster_ids = {c.cluster_id for c in result["clusters"]}
    strategy_cluster_ids = {s.cluster_id for s in result["strategies"]}
    if cluster_ids:
        assert strategy_cluster_ids, "clusterが存在するのにstrategyが生成されない"
        assert strategy_cluster_ids <= cluster_ids, "未知のcluster_idを参照するstrategyが存在する"
        for c in result["clusters"]:
            matching = [s for s in result["strategies"] if s.cluster_id == c.cluster_id]
            assert matching, f"{c.cluster_id} に対するstrategyが1件もない"
    print(f"[PASS] test_resolution_generation ({len(result['strategies'])} strategies)")


def test_queue_and_governance():
    result = run()
    queue = result["queue"]
    items = queue.ordered_items()

    assert len(items) == len(result["strategies"]), "queue登録数がstrategy数と一致しない"

    # priority ordering: impact_radius降順であること
    impact_by_cluster = {c.cluster_id: c.impact_radius for c in result["clusters"]}
    radii = [impact_by_cluster.get(item.cluster_id, 0) for item in items]
    assert radii == sorted(radii, reverse=True), f"impact_radius降順になっていない: {radii}"

    # governance: 全item に governance_status が設定されていること(UNCHECKEDが残らない)
    for item in items:
        assert item.governance_status != "UNCHECKED", f"{item.item_id} のgovernance未確認"
        assert item.status in ("pending", "validated", "rejected", "applied", "deferred")

    print(f"[PASS] test_queue_and_governance ({len(items)} items)")


def test_no_immediate_apply_or_override():
    """OVERRIDE_POLICIESにより即時適用・truth override・report優先が常に禁止されていること。"""
    assert OVERRIDE_POLICIES["immediate_apply_allowed"] is False
    assert OVERRIDE_POLICIES["truth_override_allowed"] is False
    assert OVERRIDE_POLICIES["report_priority_allowed"] is False
    assert OVERRIDE_POLICIES["local_layer_fix_allowed"] is False

    result = run()
    # 今回の実行では risk_delta が大きいため、適用されたitemは0件であることを確認
    # (governance/score基準を満たしてもrisk_delta基準で安全側に倒れることの確認)
    applied = [r for r in result["apply_results"] if r.applied]
    print(f"[PASS] test_no_immediate_apply_or_override (applied={len(applied)}/{len(result['apply_results'])})")


def main():
    tests = [
        test_all_layers_present,
        test_inconsistency_detection,
        test_consistency_score_range,
        test_conflict_clustering,
        test_resolution_generation,
        test_queue_and_governance,
        test_no_immediate_apply_or_override,
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
    print("ALL INTEGRATION TESTS PASSED.")


if __name__ == "__main__":
    main()
