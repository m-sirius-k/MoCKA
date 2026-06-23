"""
canonical_trace_id merger - Phase 5-B rev.2 (template-safe semantic convergence)

Rev.2 differs from rev.1 (canonical_trace_merger_phase5b.py) in exactly one
way: how time is used.

Rev.1 problem: a flat 1-hour adjacency cutoff for ALL pairs kept compression
low (8506 -> 6751). The natural fix -- blend time into the weighted score,
or drop it -- was rejected, because dropping the time cutoff lets recurring
template strings (e.g. "BEE_DAILY_SCAN", the same string repeated hundreds
of times across months, per TRACE_ID_CLASSIFICATION_RULES_v1 Section 5.1
"VALID_CANDIDATE" findings) merge across arbitrarily distant time points
purely on text similarity -- recreating exactly the pathology that made the
old raw `trace_id` column meaningless.

Rev.2 fix: time plays two distinct roles, never summed into the weighted
score:
  1. HARD FILTER -- only applied to detected templates (recurring,
     digit-collapsed-identical titles). Template pairs more than 24h apart
     are never even considered as merge candidates, full stop.
  2. SOFT FEATURE -- a multiplicative time-decay factor (exp(-gap/86400))
     applied AFTER the rule+vector weighted score, not mixed into it. This
     softens (never strengthens) the merge decision as time grows, without
     ever overriding the hard filter for templates.

Non-template (unique-looking) titles keep rev.1's original treatment:
session/fallback time-adjacency with a 1-hour candidate-generation cap, to
keep compute tractable.

Scope unchanged from rev.1: local TF-IDF only, no external API, no
events.db write, no PHI-OS Event Gate integration, llm_adjustment fixed at
0.0 (deferred).

Run:
    python tools/canonical_trace_merger_phase5b_v2.py
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
TRACE_ROOT = ROOT / "canonical" / "trace"
OUT_DIR = ROOT / "canonical" / "trace" / "_phase5b_v2"

MERGE_THRESHOLD = 0.65
NON_TEMPLATE_MAX_GAP_SECONDS = 3600     # unchanged from rev.1
TEMPLATE_HARD_FILTER_SECONDS = 86400    # 24h hard cutoff for template pairs
TEMPLATE_MIN_GROUP_SIZE = 3             # signature must recur >=3x to count as a template


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
        cur.execute(
            f"SELECT event_id, title, what_type, ai_actor, who_actor, change_type "
            f"FROM events WHERE event_id IN ({placeholders})",
            chunk,
        )
        for row in cur.fetchall():
            meta[row[0]] = {
                "title": row[1] or "",
                "what_type": row[2],
                "ai_actor": row[3] or row[4],
                "change_type": row[5],
            }
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
    t = re.sub(r"\d+", "#", t)
    return t


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


def rule_score(meta_a, meta_b):
    signals = []
    if meta_a["what_type"] and meta_b["what_type"]:
        signals.append(1.0 if meta_a["what_type"] == meta_b["what_type"] else 0.0)
    if meta_a["ai_actor"] and meta_b["ai_actor"]:
        signals.append(1.0 if meta_a["ai_actor"] == meta_b["ai_actor"] else 0.0)
    if meta_a["change_type"] and meta_b["change_type"]:
        signals.append(1.0 if meta_a["change_type"] == meta_b["change_type"] else 0.0)
    if not signals:
        return 0.0
    return sum(signals) / len(signals)


def parse_ts_naive(ts):
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt


class UnionFind:
    def __init__(self, items):
        self.parent = {x: x for x in items}

    def find(self, x):
        while self.parent[x] != x:
            x = self.parent[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[ra] = rb


def cluster_route(recs):
    return recs[0]["route"]


def cluster_session(recs):
    return recs[0]["session_id"]


def cluster_bounds(recs):
    return recs[0]["source_when_ts"], recs[-1]["source_when_ts"]


def build_candidate_pairs(clusters, meta):
    """Two routes: template pairs (signature-grouped, 24h hard filter) and
    non-template pairs (session/fallback time-adjacency, 1h cap, unchanged
    from rev.1)."""
    cid_signature = {}
    for cid, recs in clusters.items():
        eid_first = recs[0]["event_id"]
        title = meta.get(eid_first, {}).get("title", "")
        cid_signature[cid] = template_signature(title)

    sig_groups = defaultdict(list)
    for cid, sig in cid_signature.items():
        sig_groups[sig].append(cid)

    template_pairs = []
    non_template_cids = set()
    for sig, cids in sig_groups.items():
        if len(cids) < TEMPLATE_MIN_GROUP_SIZE or not sig:
            non_template_cids.update(cids)
            continue
        ordered = sorted(cids, key=lambda c: clusters[c][0]["source_when_ts"])
        for cid_a, cid_b in zip(ordered, ordered[1:]):
            _, end_a = cluster_bounds(clusters[cid_a])
            start_b, _ = cluster_bounds(clusters[cid_b])
            gap = (parse_ts_naive(start_b) - parse_ts_naive(end_a)).total_seconds()
            if gap <= TEMPLATE_HARD_FILTER_SECONDS:
                template_pairs.append((cid_a, cid_b, gap, "template"))
            # else: hard-filtered out, never a candidate

    groups = defaultdict(list)
    for cid in non_template_cids:
        recs = clusters[cid]
        route = cluster_route(recs)
        sid = cluster_session(recs)
        start, end = cluster_bounds(recs)
        if route == "session":
            key = ("session", sid)
        else:
            key = ("fallback", start[:10] if start else "unknown")
        groups[key].append((cid, start, end))

    non_template_pairs = []
    for key, members in groups.items():
        members.sort(key=lambda m: m[1])
        for (cid_a, _, end_a), (cid_b, start_b, _) in zip(members, members[1:]):
            gap = (parse_ts_naive(start_b) - parse_ts_naive(end_a)).total_seconds()
            if gap <= NON_TEMPLATE_MAX_GAP_SECONDS:
                non_template_pairs.append((cid_a, cid_b, gap, "non_template"))

    return template_pairs + non_template_pairs


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)

    records = load_phase5a_records()
    clusters = build_clusters(records)

    all_event_ids = {recs[0]["event_id"] for recs in clusters.values()} | \
                     {recs[-1]["event_id"] for recs in clusters.values()}
    meta = fetch_event_meta(con, all_event_ids)
    con.close()

    pairs = build_candidate_pairs(clusters, meta)

    boundary_event_ids = set()
    for cid_a, cid_b, _, _ in pairs:
        boundary_event_ids.add(clusters[cid_a][-1]["event_id"])
        boundary_event_ids.add(clusters[cid_b][0]["event_id"])

    corpus_tokens = {eid: bigrams(meta[eid]["title"]) for eid in boundary_event_ids if eid in meta}
    idf = build_idf(list(corpus_tokens.values()))
    vectors = {eid: tfidf_vector(toks, idf) for eid, toks in corpus_tokens.items()}

    uf = UnionFind(list(clusters.keys()))
    merge_graph = []
    for cid_a, cid_b, gap, pair_type in pairs:
        eid_a = clusters[cid_a][-1]["event_id"]
        eid_b = clusters[cid_b][0]["event_id"]
        if eid_a not in meta or eid_b not in meta:
            continue
        r_score = rule_score(meta[eid_a], meta[eid_b])
        v_score = cosine(vectors.get(eid_a, {}), vectors.get(eid_b, {}))
        llm_adjustment = 0.0  # deferred
        base_score = r_score * 0.4 + v_score * 0.4  # llm term contributes 0
        time_decay_factor = math.exp(-gap / 86400.0)
        final_score = base_score * time_decay_factor
        merged = final_score >= MERGE_THRESHOLD
        if merged:
            uf.union(cid_a, cid_b)
        merge_graph.append({
            "cluster_a": cid_a, "cluster_b": cid_b, "gap_seconds": gap,
            "pair_type": pair_type, "rule_score": r_score, "vector_score": v_score,
            "llm_adjustment": llm_adjustment, "base_score": base_score,
            "time_decay_factor": time_decay_factor, "final_score": final_score,
            "merged": merged,
        })

    compressed = defaultdict(list)
    for cid, recs in clusters.items():
        root = uf.find(cid)
        compressed[root].extend(r["event_id"] for r in recs)

    final_clusters = {}
    for root in set(uf.find(c) for c in clusters):
        member_cids = sorted(c for c in clusters if uf.find(c) == root)
        new_id = hashlib.sha256("|".join(member_cids).encode("utf-8")).hexdigest()[:16]
        event_ids = []
        for c in member_cids:
            event_ids.extend(r["event_id"] for r in clusters[c])
        final_clusters[new_id] = sorted(set(event_ids))

    with open(OUT_DIR / "compressed_canonical_clusters.json", "w", encoding="utf-8") as f:
        json.dump(final_clusters, f, ensure_ascii=False, indent=2)
    with open(OUT_DIR / "merge_graph.json", "w", encoding="utf-8") as f:
        json.dump(merge_graph, f, ensure_ascii=False, indent=2)
    with open(OUT_DIR / "embedding_index.json", "w", encoding="utf-8") as f:
        json.dump(vectors, f, ensure_ascii=False)

    n_template_pairs = sum(1 for p in pairs if p[3] == "template")
    n_non_template_pairs = sum(1 for p in pairs if p[3] == "non_template")
    report = {
        "input_clusters_phase5a": len(clusters),
        "template_pairs_evaluated": n_template_pairs,
        "non_template_pairs_evaluated": n_non_template_pairs,
        "merges_applied": sum(1 for m in merge_graph if m["merged"]),
        "merges_applied_template": sum(1 for m in merge_graph if m["merged"] and m["pair_type"] == "template"),
        "merges_applied_non_template": sum(1 for m in merge_graph if m["merged"] and m["pair_type"] == "non_template"),
        "output_clusters_phase5b_v2": len(final_clusters),
        "template_hard_filter_seconds": TEMPLATE_HARD_FILTER_SECONDS,
        "non_template_max_gap_seconds": NON_TEMPLATE_MAX_GAP_SECONDS,
        "template_min_group_size": TEMPLATE_MIN_GROUP_SIZE,
        "llm_adjustment_status": "deferred (fixed at 0.0), not invoked in this pass",
    }
    with open(OUT_DIR / "TCL_clean_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
