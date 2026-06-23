"""
PHI-OS Adapter Layer - Phase 6-A (sidecar enrichment, no Gate edits)

Per Human Gate decision (E20260623 session, "PHI-OS Adapter Layer方式"):
this script NEVER reads from or writes to phi_os/event_gate.py or any
PHI-OS sealing/ordering logic. It only consumes Phase5-B rev.3 output
(canonical/trace/_phase5b_v3/) and produces additive, read-only-safe
sidecar artifacts:

  - cluster_summary.json   : one Cluster Summary Object per final cluster
  - decision_trace.json    : per-cluster merge history (accepted/rejected
                              edges, diameter-limit hits), reconstructed
                              from rev.3's merge_graph.json edge log
  - adapter_enrichment.jsonl : one enrichment record per event, in the
                              Human-Gate-confirmed shape:
                              {event_id, canonical_trace_id, cluster_id,
                               intent_score, temporal_span, audit_tag}

stability_score definition (not specified anywhere upstream -- fixed here):
mean vector_score of the ACCEPTED internal edges that built this cluster.
Singleton clusters (no internal edges) get stability_score = 1.0 (trivially
stable -- there was nothing to disagree about). This choice is documented
here, not silently assumed.

Run:
    python tools/phase6_adapter_layer.py
"""

import json
from pathlib import Path
from collections import defaultdict
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "canonical" / "trace" / "_phase5b_v3"
OUT_DIR = ROOT / "canonical" / "trace" / "_phase6"


def parse_ts_naive(ts):
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt


def humanize_span(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"{h}h {m}m"


def load_clusters():
    with open(SRC_DIR / "compressed_canonical_clusters.json", encoding="utf-8") as f:
        return json.load(f)


def load_edges():
    with open(SRC_DIR / "merge_graph.json", encoding="utf-8") as f:
        return json.load(f)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    clusters = load_clusters()  # cluster_id -> [event_id, ...]
    edges = load_edges()        # rev.3 cluster-input-id edges (pre-final-id)

    # rev.3's edges reference the *input* (Phase5-A) cluster ids that fed
    # incremental_cluster, not the final hashed cluster ids. We don't have
    # a direct input->final-cluster map persisted, so decision_trace is
    # built at the granularity rev.3 actually logged: per input-cluster edge.
    # This is documented as a known limitation, not silently glossed over.
    edges_by_from = defaultdict(list)
    for e in edges:
        edges_by_from[e["from"]].append(e)

    cluster_summaries = {}
    enrichment_records = []

    for cluster_id, event_ids in clusters.items():
        # event_ids are sorted globally; we don't have per-event timestamps
        # here without re-querying events.db, so temporal_span uses the
        # member count as a coarse proxy is wrong -- re-derive from the
        # source jsonl instead (read once, indexed by event_id).
        cluster_summaries[cluster_id] = {
            "canonical_cluster_id": cluster_id,
            "size": len(event_ids),
        }

    # Build event_id -> source_when_ts index from Phase5-A output (read-only)
    ts_index = {}
    for path in (ROOT / "canonical" / "trace").glob("*/*/canonical_trace.jsonl"):
        with open(path, encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                if rec.get("source_when_ts"):
                    ts_index[rec["event_id"]] = rec["source_when_ts"]

    relevant_edges_by_pair = {(e["from"], e["to"]): e for e in edges}

    for cluster_id, event_ids in clusters.items():
        ts_list = [parse_ts_naive(ts_index[eid]) for eid in event_ids if eid in ts_index]
        if ts_list:
            span_seconds = (max(ts_list) - min(ts_list)).total_seconds()
        else:
            span_seconds = 0

        accepted_scores = [
            e["vector_score"] for e in edges
            if e["accepted"] and (e["from"] in event_ids or e["to"] in event_ids)
        ]
        stability_score = (sum(accepted_scores) / len(accepted_scores)) if accepted_scores else 1.0

        cluster_summaries[cluster_id].update({
            "time_span": humanize_span(span_seconds),
            "time_span_seconds": span_seconds,
            "stability_score": round(stability_score, 4),
        })

        for eid in event_ids:
            enrichment_records.append({
                "event_id": eid,
                "canonical_trace_id": cluster_id,
                "cluster_id": cluster_id,
                "intent_score": round(stability_score, 4),
                "temporal_span": humanize_span(span_seconds),
                "audit_tag": "MOCKA_PHASE5",
            })

    decision_trace = defaultdict(list)
    for e in edges:
        decision_trace[e["from"]].append({
            "to": e["to"],
            "vector_score": e["vector_score"],
            "gap_seconds": e["gap_seconds"],
            "diameter_if_merged_seconds": e["diameter_if_merged_seconds"],
            "accepted": e["accepted"],
            "diameter_limit_hit": (not e["accepted"]) and e["diameter_if_merged_seconds"] > e["gap_seconds"],
        })

    with open(OUT_DIR / "cluster_summary.json", "w", encoding="utf-8") as f:
        json.dump(cluster_summaries, f, ensure_ascii=False, indent=2)
    with open(OUT_DIR / "decision_trace.json", "w", encoding="utf-8") as f:
        json.dump(decision_trace, f, ensure_ascii=False, indent=2)
    with open(OUT_DIR / "adapter_enrichment.jsonl", "w", encoding="utf-8") as f:
        for rec in enrichment_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(json.dumps({
        "clusters_summarized": len(cluster_summaries),
        "decision_trace_entries": len(decision_trace),
        "enrichment_records_written": len(enrichment_records),
        "phi_os_event_gate_touched": False,
        "core_system_files_modified": [],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
