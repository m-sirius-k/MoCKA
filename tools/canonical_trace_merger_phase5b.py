"""
canonical_trace_id merger - Phase 5-B (semantic convergence)

Scope (per Phase4 Step4/5 decisions and the Phase5-B execution instruction):
  - Input: Phase 5-A output (canonical/trace/**/canonical_trace.jsonl),
    excluding the _invalid bucket.
  - TCL (Time Clean Layer): records with no valid source_when_ts are
    excluded from clustering entirely (already isolated by Phase 5-A).
  - Embedding: local character-bigram TF-IDF + cosine similarity. No
    sklearn, no external API, no new pip install (confirmed by Human Gate
    after checking environment: sentence_transformers/openai not installed,
    OpenAI key present but unused -- no external network calls are made).
  - intent_match = rule_score*0.4 + vector_score*0.4 + llm_adjustment*0.2,
    with llm_adjustment fixed at 0.0 in this pass. Real LLM-based conflict
    resolution is explicitly deferred -- calling an LLM at this volume is
    itself a cost/external-dependency decision and was not confirmed in
    this pass. This is a known, documented gap, not a silent omission.
  - Embedding vectors are computed per boundary EVENT, never averaged at
    the canonical-cluster level (explicit constraint from Phase4 Step4).
  - Adjacency for merge candidates is restricted to same-day pairs with a
    gap <= 3600 seconds. This 1-hour sanity cap was not specified in the
    Phase5-B instruction; it is an addition by this implementation to
    prevent semantically meaningless merges across distant points in time,
    and is recorded here explicitly rather than applied silently.
  - No write to events.db. No PHI-OS Event Gate integration.

Run:
    python tools/canonical_trace_merger_phase5b.py
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
OUT_DIR = ROOT / "canonical" / "trace" / "_phase5b"

MERGE_THRESHOLD = 0.65
ADJACENCY_MAX_GAP_SECONDS = 3600  # implementation-added sanity cap, see module docstring


def load_phase5a_records():
    records = []
    for path in TRACE_ROOT.glob("*/*/canonical_trace.jsonl"):
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


def cluster_route(cluster_records):
    return cluster_records[0]["route"]


def cluster_session(cluster_records):
    return cluster_records[0]["session_id"]


def cluster_bounds(cluster_records):
    return cluster_records[0]["source_when_ts"], cluster_records[-1]["source_when_ts"]


def parse_ts_naive(ts):
    """Some when_ts values mix tz-aware and tz-naive ISO strings. Normalize
    to naive UTC for gap arithmetic only -- not written back anywhere."""
    dt = datetime.fromisoformat(ts)
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt


# ---------------- TF-IDF (char-bigram, pure python) ----------------

def normalize_text(text):
    return re.sub(r"\s+", " ", text.strip().lower())


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
    idf = {term: math.log((n_docs + 1) / (count + 1)) + 1.0 for term, count in df.items()}
    return idf


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


# ---------------- rule_score (reused logic from Phase5-A) ----------------

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


# ---------------- adjacency + union-find ----------------

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


def build_adjacency_pairs(clusters):
    """Group clusters by (route, session_id or date), order by time, pair consecutive."""
    groups = defaultdict(list)
    for cid, recs in clusters.items():
        route = cluster_route(recs)
        sid = cluster_session(recs)
        start, end = cluster_bounds(recs)
        if route == "session":
            key = ("session", sid)
        else:
            date_key = start[:10] if start else "unknown"
            key = ("fallback", date_key)
        groups[key].append((cid, start, end))

    pairs = []
    for key, members in groups.items():
        members.sort(key=lambda m: m[1])
        for (cid_a, _, end_a), (cid_b, start_b, _) in zip(members, members[1:]):
            gap = (parse_ts_naive(start_b) - parse_ts_naive(end_a)).total_seconds()
            if gap <= ADJACENCY_MAX_GAP_SECONDS:
                pairs.append((cid_a, cid_b, gap))
    return pairs


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)

    records = load_phase5a_records()
    clusters = build_clusters(records)
    pairs = build_adjacency_pairs(clusters)

    boundary_event_ids = set()
    for cid_a, cid_b, _ in pairs:
        boundary_event_ids.add(clusters[cid_a][-1]["event_id"])
        boundary_event_ids.add(clusters[cid_b][0]["event_id"])
    meta = fetch_event_meta(con, boundary_event_ids)
    con.close()

    corpus_tokens = {eid: bigrams(meta[eid]["title"]) for eid in boundary_event_ids if eid in meta}
    idf = build_idf(list(corpus_tokens.values()))
    vectors = {eid: tfidf_vector(toks, idf) for eid, toks in corpus_tokens.items()}

    uf = UnionFind(list(clusters.keys()))
    merge_graph = []
    for cid_a, cid_b, gap in pairs:
        eid_a = clusters[cid_a][-1]["event_id"]
        eid_b = clusters[cid_b][0]["event_id"]
        if eid_a not in meta or eid_b not in meta:
            continue
        r_score = rule_score(meta[eid_a], meta[eid_b])
        v_score = cosine(vectors.get(eid_a, {}), vectors.get(eid_b, {}))
        llm_adjustment = 0.0  # deferred, see module docstring
        intent_match = r_score * 0.4 + v_score * 0.4 + llm_adjustment * 0.2
        merged = intent_match >= MERGE_THRESHOLD
        if merged:
            uf.union(cid_a, cid_b)
        merge_graph.append({
            "cluster_a": cid_a, "cluster_b": cid_b, "gap_seconds": gap,
            "rule_score": r_score, "vector_score": v_score,
            "llm_adjustment": llm_adjustment, "intent_match": intent_match,
            "merged": merged,
        })

    compressed = defaultdict(list)
    for cid, recs in clusters.items():
        root = uf.find(cid)
        compressed[root].extend(r["event_id"] for r in recs)

    final_clusters = {}
    for root, event_ids in compressed.items():
        member_roots = sorted({uf.find(c) for c in clusters if uf.find(c) == root})
        new_id = hashlib.sha256(("|".join(sorted(set(
            cid for cid in clusters if uf.find(cid) == root
        )))).encode("utf-8")).hexdigest()[:16]
        final_clusters[new_id] = sorted(set(event_ids))

    with open(OUT_DIR / "compressed_canonical_clusters.json", "w", encoding="utf-8") as f:
        json.dump(final_clusters, f, ensure_ascii=False, indent=2)

    with open(OUT_DIR / "merge_graph.json", "w", encoding="utf-8") as f:
        json.dump(merge_graph, f, ensure_ascii=False, indent=2)

    # embedding_index: JSON, not .bin -- chosen deliberately for auditability
    # (MoCKA Explainability principle, EVENT_FOUNDATION_v1 P2), documented
    # as a deviation from the literal Phase5-B output spec.
    with open(OUT_DIR / "embedding_index.json", "w", encoding="utf-8") as f:
        json.dump({eid: vectors[eid] for eid in vectors}, f, ensure_ascii=False)

    invalid_count = sum(
        1 for path in TRACE_ROOT.glob("**/canonical_trace.jsonl")
        for line in open(path, encoding="utf-8")
        if json.loads(line)["route"] == "invalid_timestamp"
    )
    tcl_report = {
        "input_records": len(records),
        "input_clusters_phase5a": len(clusters),
        "adjacency_pairs_evaluated": len(pairs),
        "merges_applied": sum(1 for m in merge_graph if m["merged"]),
        "output_clusters_phase5b": len(final_clusters),
        "invalid_timestamp_excluded": invalid_count,
        "adjacency_max_gap_seconds": ADJACENCY_MAX_GAP_SECONDS,
        "llm_adjustment_status": "deferred (fixed at 0.0), not invoked in this pass",
    }
    with open(OUT_DIR / "TCL_clean_report.json", "w", encoding="utf-8") as f:
        json.dump(tcl_report, f, ensure_ascii=False, indent=2)

    print(json.dumps(tcl_report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
