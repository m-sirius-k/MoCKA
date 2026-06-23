"""
canonical_trace_id merger - Phase 5-B rev.3 (diameter-constrained clustering)

Rev.3 replaces Union-Find with incremental local clustering, to fix a
structural flaw found in rev.2's statistics: Union-Find's transitive
closure let chains of pairwise-valid merges (A-B within 6h, B-C within 6h)
produce a final cluster spanning far more than the intended time window
(observed: a 275-event cluster). Each individual edge respected the time
cap, but the resulting connected component did not.

Rev.3 algorithm change (per Human Gate instruction):
  - No Union-Find. No transitive connectivity.
  - Within each candidate group (a template-signature group, or a
    session/fallback adjacency group for non-template titles -- same
    grouping as rev.2), clusters are grown incrementally in time order.
  - A candidate cluster only ABSORBS the next item if ALL of:
      1. vector_score (TF-IDF cosine, boundary events) >= 0.65
      2. gap to the previous member <= 6h (21600s) -- replaces rev.2's
         24h template hard filter
      3. diameter check: (candidate_end - cluster_start) <= 6h (21600s) --
         this is the new constraint that rev.2 lacked. It is evaluated
         against the ORIGINAL start of the growing cluster, not just the
         previous member, so no chain can silently exceed the window.
  - If any condition fails, the current cluster closes and a new one
    starts at the candidate.

This makes "long-range accidental merge" structurally impossible: every
output cluster's time span is bounded by construction, not by hoping no
chain forms.

Scope unchanged: local TF-IDF only, no external API, no events.db write,
no PHI-OS Event Gate integration, llm_adjustment not used in the edge test
(rule_score also dropped from the edge test per this revision's simplified
gate -- see Section 3 of the Human Gate instruction: edge depends on
embedding_similarity + template/group consistency + hard time limit only).

Run:
    python tools/canonical_trace_merger_phase5b_v3.py
"""

import json
import sqlite3
import hashlib
import re
import math
from pathlib import Path
from collections import defaultdict
from datetime import datetime

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "mocka_events.db"
OUT_DIR = ROOT / "canonical" / "trace" / "_phase5b_v3"

SIM_THRESHOLD = 0.65
HARD_LIMIT_SECONDS = 6 * 3600       # replaces rev.2's 24h template filter
DIAMETER_LIMIT_SECONDS = 6 * 3600   # new: bounds the whole cluster, not just adjacent pairs
TEMPLATE_MIN_GROUP_SIZE = 3


def load_phase5a_records():
    records = []
    for path in (ROOT / "canonical" / "trace").glob("*/*/canonical_trace.jsonl"):
        with open(path, encoding="utf-8") as f:
            for line in f:
                rec = json.loads(line)
                if rec["route"] == "invalid_timestamp":
                    continue
                records.append(rec)
    return records


def fetch_event_meta(con, event_ids):
    cur = con.cursor()
    meta = {}
    ids = list(event_ids)
    for i in range(0, len(ids), 500):
        chunk = ids[i:i + 500]
        placeholders = ",".join("?" for _ in chunk)
        cur.execute(f"SELECT event_id, title FROM events WHERE event_id IN ({placeholders})", chunk)
        for row in cur.fetchall():
            meta[row[0]] = {"title": row[1] or ""}
    return meta


def build_clusters(records):
    clusters = defaultdict(list)
    for rec in records:
        clusters[rec["canonical_trace_id"]].append(rec)
    for cid in clusters:
        clusters[cid].sort(key=lambda r: r["source_when_ts"])
    return clusters


def normalize_text(text):
    return re.sub(r"\s+", " ", text.strip().lower())


def template_signature(title):
    t = normalize_text(title)
    return re.sub(r"\d+", "#", t)


def bigrams(text):
    text = normalize_text(text)
    if len(text) < 2:
        return [text] if text else []
    return [text[i:i + 2] for i in range(len(text) - 1)]


def build_idf(corpus_tokens):
    df = defaultdict(int)
    n_docs = len(corpus_tokens)
    for tokens in corpus_tokens:
        for term in set(tokens):
            df[term] += 1
    return {term: math.log((n_docs + 1) / (count + 1)) + 1.0 for term, count in df.items()}


def tfidf_vector(tokens, idf):
    tf = defaultdict(int)
    for term in tokens:
        tf[term] += 1
    vec = {}
    for term, count in tf.items():
        if term in idf:
            vec[term] = count * idf[term]
    norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
    return {k: v / norm for k, v in vec.items()}


def cosine(vec_a, vec_b):
    if not vec_a or not vec_b:
        return 0.0
    common = set(vec_a) & set(vec_b)
    return sum(vec_a[k] * vec_b[k] for k in common)


def parse_ts_naive(ts):
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt


def cluster_route(recs):
    return recs[0]["route"]


def cluster_session(recs):
    return recs[0]["session_id"]


def cluster_bounds(recs):
    return recs[0]["source_when_ts"], recs[-1]["source_when_ts"]


def group_clusters(clusters, meta):
    """Same grouping policy as rev.2: template-signature groups (recurring
    titles) vs session/fallback adjacency groups (unique titles)."""
    cid_signature = {}
    for cid, recs in clusters.items():
        eid_first = recs[0]["event_id"]
        cid_signature[cid] = template_signature(meta.get(eid_first, {}).get("title", ""))

    sig_groups = defaultdict(list)
    for cid, sig in cid_signature.items():
        sig_groups[sig].append(cid)

    template_groups = []
    non_template_cids = set()
    for sig, cids in sig_groups.items():
        if len(cids) < TEMPLATE_MIN_GROUP_SIZE or not sig:
            non_template_cids.update(cids)
            continue
        template_groups.append(sorted(cids, key=lambda c: clusters[c][0]["source_when_ts"]))

    adjacency_groups = defaultdict(list)
    for cid in non_template_cids:
        recs = clusters[cid]
        route = cluster_route(recs)
        sid = cluster_session(recs)
        start, _ = cluster_bounds(recs)
        if route == "session":
            key = ("session", sid)
        else:
            key = ("fallback", start[:10] if start else "unknown")
        adjacency_groups[key].append(cid)

    non_template_groups = [
        sorted(cids, key=lambda c: clusters[c][0]["source_when_ts"])
        for cids in adjacency_groups.values()
    ]

    return template_groups + non_template_groups


def incremental_cluster(ordered_cids, clusters, vectors):
    """Core rev.3 change: grow clusters in time order with a HARD edge gap
    limit AND a whole-cluster diameter limit. No transitive closure."""
    if not ordered_cids:
        return []
    groups = []
    current = [ordered_cids[0]]
    current_start = parse_ts_naive(cluster_bounds(clusters[ordered_cids[0]])[0])
    edges_log = []

    for prev_cid, cand_cid in zip(ordered_cids, ordered_cids[1:]):
        prev_recs = clusters[prev_cid]
        cand_recs = clusters[cand_cid]
        eid_prev_end = prev_recs[-1]["event_id"]
        eid_cand_start = cand_recs[0]["event_id"]
        sim = cosine(vectors.get(eid_prev_end, {}), vectors.get(eid_cand_start, {}))
        gap = (parse_ts_naive(cand_recs[0]["source_when_ts"]) -
               parse_ts_naive(prev_recs[-1]["source_when_ts"])).total_seconds()
        cand_end = parse_ts_naive(cand_recs[-1]["source_when_ts"])
        diameter_if_merged = (cand_end - current_start).total_seconds()

        accept = (sim >= SIM_THRESHOLD and 0 <= gap <= HARD_LIMIT_SECONDS and
                  diameter_if_merged <= DIAMETER_LIMIT_SECONDS)
        edges_log.append({
            "from": prev_cid, "to": cand_cid, "vector_score": sim, "gap_seconds": gap,
            "diameter_if_merged_seconds": diameter_if_merged, "accepted": accept,
        })

        if accept:
            current.append(cand_cid)
        else:
            groups.append(current)
            current = [cand_cid]
            current_start = parse_ts_naive(cluster_bounds(clusters[cand_cid])[0])

    groups.append(current)
    return groups, edges_log


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)

    records = load_phase5a_records()
    clusters = build_clusters(records)

    boundary_ids_for_sig = {recs[0]["event_id"] for recs in clusters.values()}
    meta_sig = fetch_event_meta(con, boundary_ids_for_sig)

    groups = group_clusters(clusters, meta_sig)

    all_boundary_ids = set()
    for cid in clusters:
        all_boundary_ids.add(clusters[cid][0]["event_id"])
        all_boundary_ids.add(clusters[cid][-1]["event_id"])
    meta = fetch_event_meta(con, all_boundary_ids)
    con.close()

    corpus_tokens = {eid: bigrams(meta[eid]["title"]) for eid in all_boundary_ids if eid in meta}
    idf = build_idf(list(corpus_tokens.values()))
    vectors = {eid: tfidf_vector(toks, idf) for eid, toks in corpus_tokens.items()}

    final_groups = []
    all_edges = []
    for ordered_cids in groups:
        sub_groups, edges = incremental_cluster(ordered_cids, clusters, vectors)
        final_groups.extend(sub_groups)
        all_edges.extend(edges)

    final_clusters = {}
    diameters = []
    for member_cids in final_groups:
        new_id = hashlib.sha256("|".join(sorted(member_cids)).encode("utf-8")).hexdigest()[:16]
        event_ids = []
        all_ts = []
        for cid in member_cids:
            for r in clusters[cid]:
                event_ids.append(r["event_id"])
                all_ts.append(parse_ts_naive(r["source_when_ts"]))
        final_clusters[new_id] = sorted(set(event_ids))
        diameters.append((max(all_ts) - min(all_ts)).total_seconds())

    with open(OUT_DIR / "compressed_canonical_clusters.json", "w", encoding="utf-8") as f:
        json.dump(final_clusters, f, ensure_ascii=False, indent=2)
    with open(OUT_DIR / "merge_graph.json", "w", encoding="utf-8") as f:
        json.dump(all_edges, f, ensure_ascii=False, indent=2)
    with open(OUT_DIR / "embedding_index.json", "w", encoding="utf-8") as f:
        json.dump(vectors, f, ensure_ascii=False)

    sizes = sorted(len(v) for v in final_clusters.values())
    over_limit = sum(1 for d in diameters if d > DIAMETER_LIMIT_SECONDS)
    report = {
        "input_clusters_phase5a": len(clusters),
        "groups_processed": len(groups),
        "edges_evaluated": len(all_edges),
        "edges_accepted": sum(1 for e in all_edges if e["accepted"]),
        "output_clusters_phase5b_v3": len(final_clusters),
        "max_cluster_size": sizes[-1] if sizes else 0,
        "singleton_clusters": sum(1 for s in sizes if s == 1),
        "max_diameter_seconds_observed": max(diameters) if diameters else 0,
        "clusters_exceeding_diameter_limit": over_limit,
        "hard_limit_seconds": HARD_LIMIT_SECONDS,
        "diameter_limit_seconds": DIAMETER_LIMIT_SECONDS,
        "algorithm": "incremental local clustering (no Union-Find, no transitive closure)",
    }
    with open(OUT_DIR / "TCL_clean_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
