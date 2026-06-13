# -*- coding: utf-8 -*-
"""Consistency Pipeline (Phase 5 Cross-Layer Consistency Engine) - CLI Entrypoint

usage:
    python -m cross_layer_consistency.consistency_pipeline

処理フロー:
    Layer Snapshots
       v
    Dependency Graph
       v
    Inconsistency Detection
       v
    Consistency Scoring
       v
    Conflict Clustering
       v
    Resolution Strategy
       v
    Queue
       v
    Governance Check
       v
    Applier
"""

from cross_layer_consistency.layer_snapshot_builder import build as build_snapshot
from cross_layer_consistency.dependency_graph_builder import build as build_graph
from cross_layer_consistency.consistency_score_engine import compute as compute_score
from cross_layer_consistency.inconsistency_detector import detect as detect_inconsistencies
from cross_layer_consistency.conflict_clusterer import cluster as cluster_conflicts
from cross_layer_consistency.resolution_strategy_engine import propose as propose_strategies
from cross_layer_consistency.consistency_queue import ConsistencyQueue
from cross_layer_consistency.consistency_applier import apply as apply_item


def run():
    snapshot = build_snapshot()
    graph = build_graph()
    score_result = compute_score(snapshot)
    inconsistencies = detect_inconsistencies(snapshot, score_result.sub_scores)
    clusters = cluster_conflicts(inconsistencies)
    strategies = propose_strategies(clusters)

    incs_by_cluster = {c.cluster_id: c.inconsistencies for c in clusters}
    impact_by_cluster = {c.cluster_id: c.impact_radius for c in clusters}

    queue = ConsistencyQueue()
    for s in strategies:
        item = queue.enqueue(s, impact_by_cluster.get(s.cluster_id, 0))
        queue.validate(item, snapshot.get("report"))

    apply_results = []
    for item in queue.ordered_items():
        cluster_incs = incs_by_cluster.get(item.cluster_id, [])
        apply_results.append(apply_item(item, score_result.total_score, cluster_incs))

    return {
        "snapshot": snapshot,
        "graph": graph,
        "score_result": score_result,
        "inconsistencies": inconsistencies,
        "clusters": clusters,
        "strategies": strategies,
        "queue": queue,
        "apply_results": apply_results,
    }


def _print(result):
    print("=" * 100)
    print("LAYER SNAPSHOTS")
    print("=" * 100)
    for name, ls in result["snapshot"].layers.items():
        print(f"  {name:<12} {ls.status}")

    print()
    print("=" * 100)
    print("DEPENDENCY GRAPH")
    print("=" * 100)
    print("  nodes:", result["graph"].nodes)
    print("  edges:", result["graph"].edges)
    print("  cycles:", result["graph"].cycles)

    print()
    print("=" * 100)
    print("CONSISTENCY SCORE")
    print("=" * 100)
    for k, v in result["score_result"].breakdown.items():
        print(f"  {k:<20} value={v['value']:<8} weight={v['weight']:<6} contribution={v['contribution']}")
    print(f"  TOTAL = {result['score_result'].total_score}")

    print()
    print("=" * 100)
    print(f"INCONSISTENCIES ({len(result['inconsistencies'])})")
    print("=" * 100)
    for inc in result["inconsistencies"]:
        print(f"  - [{inc.severity}] {inc.inconsistency_type}: {inc.layers_involved}")
        print(f"      {inc.description}")

    print()
    print("=" * 100)
    print(f"CONFLICT CLUSTERS ({len(result['clusters'])})")
    print("=" * 100)
    for c in result["clusters"]:
        print(f"  - {c.cluster_id}: layers={c.layers_involved} root_cause_candidate={c.root_cause_candidate} "
              f"impact_radius={c.impact_radius} n_inconsistencies={len(c.inconsistencies)}")

    print()
    print("=" * 100)
    print(f"RESOLUTION STRATEGIES ({len(result['strategies'])})")
    print("=" * 100)
    for s in result["strategies"]:
        print(f"  - [{s.cluster_id}] {s.strategy_type}: {s.description}")

    print()
    print("=" * 100)
    print("QUEUE")
    print("=" * 100)
    for item in result["queue"].ordered_items():
        print(f"  {item.item_id} cluster={item.cluster_id} strategy={item.strategy.strategy_type} "
              f"status={item.status} governance={item.governance_status}")

    print()
    print("=" * 100)
    print("APPLY RESULTS")
    print("=" * 100)
    for r in result["apply_results"]:
        print(f"  {r}")

    applied = [r for r in result["apply_results"] if r.applied]
    print()
    print(f"OVERALL: {len(applied)} / {len(result['apply_results'])} items applied "
          f"(immediate apply disabled by default; pending items remain in queue for deferred review)")


def main():
    result = run()
    _print(result)


if __name__ == "__main__":
    main()
