"""
canonical_trace_id generator - Phase 5-A (safe core)

Scope (per Phase4 Step4/Step5 decisions, see docs/mocka3/CANONICAL_TRACE_ID_GENERATION_RULE_v1.md
and event log entries E20260623_651337070238f / E20260623_732330081199e / E20260623_86813997434c3):

  - Reads data/mocka_events.db READ-ONLY. Never writes to it.
  - Does not touch PHI-OS Event Gate. Not wired into any live write path.
  - intent_match here is rule_score ONLY (Layer A). No embedding, no LLM
    adjustment. Those are explicitly out of scope (Phase 5-B/5-C).
  - Output is additive only: new files under canonical/trace/<yyyy>/<mm>/.
  - trace_id (raw column) is read for reference only, never reinterpreted
    as meaningful (per docs/mocka3/AUDIT_TRACE_LAYER_RULES_v1.md).

Run:
    python tools/canonical_trace_generator_phase5a.py
"""

import sqlite3
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "data" / "mocka_events.db"
OUT_ROOT = ROOT / "canonical" / "trace"

GAP_BASE_SECONDS = 180
GAP_BATCH_SECONDS = min(GAP_BASE_SECONDS * 4, 900)   # +300%, capped at 15min
GAP_CONTINUOUS_SECONDS = GAP_BASE_SECONDS * 0.5       # -50%
BATCH_ACTORS = {"claude_mcp", "TIC", "BEE", "system"}
MERGE_THRESHOLD = 0.65


def fetch_events(con):
    cur = con.cursor()
    cur.execute(
        """
        SELECT event_id, session_id, when_ts, what_type, ai_actor, who_actor,
               change_type, related_event_id, title
        FROM events
        ORDER BY session_id IS NULL, session_id, when_ts
        """
    )
    return cur.fetchall()


def parse_ts(ts):
    return datetime.fromisoformat(ts)


def try_parse_ts(ts):
    """Returns datetime or None. Some when_ts values in the dataset are not
    valid ISO timestamps (e.g. stray hash strings) -- this is a data quality
    issue independent of the trace_id contamination already documented in
    docs/mocka3/TRACE_ID_SEMANTIC_AUDIT_v1.md. Such rows are isolated, not
    dropped (see INVALID_TIMESTAMP route below)."""
    try:
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
        return None


def gap_threshold_for(prev_row, cur_row):
    actor_prev = (prev_row[4] or prev_row[5] or "").strip()
    actor_cur = (cur_row[4] or cur_row[5] or "").strip()
    if actor_prev in BATCH_ACTORS or actor_cur in BATCH_ACTORS:
        return GAP_BATCH_SECONDS
    return GAP_BASE_SECONDS


def segment_session(rows):
    """Layer 2: split one session's time-sorted rows into provisional segments."""
    segments = []
    current = [rows[0]]
    for prev, cur in zip(rows, rows[1:]):
        gap = (try_parse_ts(cur[2]) - try_parse_ts(prev[2])).total_seconds()
        threshold = gap_threshold_for(prev, cur)
        if gap <= GAP_CONTINUOUS_SECONDS:
            current.append(cur)
            continue
        if gap > threshold:
            segments.append(current)
            current = [cur]
        else:
            current.append(cur)
    segments.append(current)
    return segments


def rule_score(seg_a_last, seg_b_first):
    """Layer 3, Layer A only: rule-based match score, 0.0-1.0."""
    signals = []
    if seg_a_last[3] and seg_b_first[3]:
        signals.append(1.0 if seg_a_last[3] == seg_b_first[3] else 0.0)  # what_type
    actor_a = seg_a_last[4] or seg_a_last[5]
    actor_b = seg_b_first[4] or seg_b_first[5]
    if actor_a and actor_b:
        signals.append(1.0 if actor_a == actor_b else 0.0)
    if seg_a_last[6] and seg_b_first[6]:
        signals.append(1.0 if seg_a_last[6] == seg_b_first[6] else 0.0)  # change_type
    if not signals:
        return 0.0
    return sum(signals) / len(signals)


def merge_segments(segments):
    """Layer 3: merge adjacent segments with rule_score >= MERGE_THRESHOLD."""
    clusters = [segments[0]]
    scores = [None]
    for seg in segments[1:]:
        prev_cluster = clusters[-1]
        score = rule_score(prev_cluster[-1], seg[0])
        if score >= MERGE_THRESHOLD:
            prev_cluster.extend(seg)
            scores.append(score)
        else:
            clusters.append(seg)
            scores.append(score)
    return clusters


def canonical_id(session_key, cluster_index):
    raw = f"{session_key}:{cluster_index}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def fallback_cluster_key(ts_iso):
    dt = try_parse_ts(ts_iso)
    return f"NOSESSION_{dt.strftime('%Y%m%d%H%M')}"  # 1-minute granularity


def process(rows):
    """Returns list of output records. Does not write anything."""
    records = []

    by_session = {}
    no_session = []
    invalid_ts_rows = []
    for row in rows:
        if try_parse_ts(row[2]) is None:
            invalid_ts_rows.append(row)
            continue
        sid = row[1]
        if sid and sid.strip():
            by_session.setdefault(sid, []).append(row)
        else:
            no_session.append(row)

    now_iso = datetime.now(timezone.utc).isoformat()
    for r in invalid_ts_rows:
        records.append({
            "event_id": r[0],
            "session_id": r[1],
            "raw_trace_id_ref": None,
            "canonical_trace_id": canonical_id("INVALID_TIMESTAMP", 0),
            "cluster_index": 0,
            "route": "invalid_timestamp",
            "generator_version": "phase5a_rule_only",
            "generated_at": now_iso,
            "source_when_ts": None,
            "raw_when_ts_value": r[2],
        })

    # session_id route (Layer1 base -> Layer2 -> Layer3)
    for session_id, session_rows in by_session.items():
        session_rows = sorted(session_rows, key=lambda r: r[2])
        segments = segment_session(session_rows)
        clusters = merge_segments(segments)
        for cluster_index, cluster_rows in enumerate(clusters):
            cid = canonical_id(session_id, cluster_index)
            for r in cluster_rows:
                records.append({
                    "event_id": r[0],
                    "session_id": session_id,
                    "raw_trace_id_ref": None,  # filled by caller if needed
                    "canonical_trace_id": cid,
                    "cluster_index": cluster_index,
                    "route": "session",
                    "generator_version": "phase5a_rule_only",
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "source_when_ts": r[2],
                })

    # session_id-less fallback: 1-minute timestamp clustering, no merge step
    fallback_groups = {}
    for row in no_session:
        key = fallback_cluster_key(row[2])
        fallback_groups.setdefault(key, []).append(row)
    for key, group_rows in fallback_groups.items():
        cid = canonical_id(key, 0)
        for r in group_rows:
            records.append({
                "event_id": r[0],
                "session_id": None,
                "raw_trace_id_ref": None,
                "canonical_trace_id": cid,
                "cluster_index": 0,
                "route": "fallback_timestamp_1min",
                "generator_version": "phase5a_rule_only",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source_when_ts": r[2],
            })

    return records


def write_records(records):
    """Additive append-only write, grouped by each event's own when_ts month."""
    written = 0
    by_month = {}
    for rec in records:
        if rec["source_when_ts"] is None:
            key = ("_invalid", None)
        else:
            dt = try_parse_ts(rec["source_when_ts"])
            key = (dt.strftime("%Y"), dt.strftime("%m"))
        by_month.setdefault(key, []).append(rec)

    for (yyyy, mm), recs in by_month.items():
        out_dir = OUT_ROOT / yyyy if mm is None else OUT_ROOT / yyyy / mm
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "canonical_trace.jsonl"
        with open(out_path, "a", encoding="utf-8") as f:
            for rec in recs:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                written += 1
    return written


def main():
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    try:
        rows = fetch_events(con)
    finally:
        con.close()

    records = process(rows)
    written = write_records(records)

    n_sessions = len({r[1] for r in rows if r[1]})
    n_clusters = len({rec["canonical_trace_id"] for rec in records})
    print(f"input_events={len(rows)}")
    print(f"distinct_session_ids={n_sessions}")
    print(f"output_records_written={written}")
    print(f"distinct_canonical_trace_id={n_clusters}")


if __name__ == "__main__":
    main()
