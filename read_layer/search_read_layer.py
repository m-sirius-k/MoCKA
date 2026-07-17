# W-4 read layer: token search (v2) added alongside production v1, comparison-preserving.
# DC_20260714_001. Non-destructive: read-only, v1 untouched (source of truth remains
# mocka_mcp_server.py:search_events). token_search is a pure function.
#
# Scope (approved): new read-layer code, token search function, traversal function.
# Prohibited: schema change, migration, existing-event edit, ledger change, v1 removal.
import sqlite3

# Mirror of production v1 field set (mocka_mcp_server.py:166). Kept in sync manually;
# this module never imports or mutates the server.
PRIMARY_FIELDS = ["title", "short_summary", "description", "free_note",
                  "why_purpose", "who_actor", "what_type", "how_trigger"]


def _get(row, f):
    try:
        v = row[f]
    except (KeyError, IndexError):
        return ""
    return "" if v is None else str(v)


def v1_mirror(rows, query):
    """Read-only mirror of production v1 (whole-phrase, single-field substring) for
    parity comparison ONLY. Source of truth stays mocka_mcp_server.py:search_events."""
    q = query.lower()
    scored = []
    for r in rows:
        score = 0
        for f in PRIMARY_FIELDS:
            val = _get(r, f).lower()
            if q in val:
                score += 10
                if val.startswith(q):
                    score += 5
        if _get(r, "what_type") == "user_voice":
            score = max(0, score - 8)
        if score > 0:
            scored.append((score, r))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:30]]


def token_search(rows, query):
    """W-4 v2: token AND across concatenated primary fields. Pure function.
    A row matches when every whitespace-separated token is present."""
    tokens = [t for t in query.lower().split() if t]
    if not tokens:
        return []
    scored = []
    for r in rows:
        blob = " ".join(_get(r, f).lower() for f in PRIMARY_FIELDS)
        if all(t in blob for t in tokens):
            score = sum(blob.count(t) for t in tokens)
            if _get(r, "what_type") == "user_voice":
                score = max(0, score - 8)
            if score > 0:
                scored.append((score, r))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [r for _, r in scored[:30]]


def relationship_traversal(row, fetch_by_id, hops=1):
    """W-4: bounded relationship expansion. Follows related_event_id one hop by default.
    hops is hard-capped to avoid recursion/runaway. fetch_by_id(id)->row_or_None."""
    hops = max(0, min(int(hops), 1))  # hard cap 1 hop in this read layer
    chain = []
    current = row
    for _ in range(hops):
        rel = _get(current, "related_event_id")
        if not rel:
            break
        nxt = fetch_by_id(rel)
        chain.append({"related_event_id": rel, "found": nxt is not None,
                      "event_id": (_get(nxt, "event_id") if nxt else None)})
        if nxt is None:
            break
        current = nxt
    return chain


def compare(rows, query):
    """Comparison-preserving helper: run v1 mirror and v2 side by side."""
    v1 = v1_mirror(rows, query)
    v2 = token_search(rows, query)
    v1_ids = [_get(r, "event_id") for r in v1]
    v2_ids = [_get(r, "event_id") for r in v2]
    return {
        "query": query,
        "v1_hits": len(v1), "v2_hits": len(v2),
        "v1_ids": v1_ids[:10], "v2_ids": v2_ids[:10],
        "recovered_by_v2": [i for i in v2_ids if i not in v1_ids],
    }


def open_events_readonly(db_path):
    """Read-only connection: mode=ro + PRAGMA query_only. Writes are rejected."""
    con = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA query_only=ON")
    return con


def load_rows(con):
    cols = ", ".join(["event_id"] + [f for f in PRIMARY_FIELDS if f != "description"] + ["related_event_id", "trace_id"])
    return con.execute(f"SELECT {cols} FROM events").fetchall()


if __name__ == "__main__":
    # Read-only self-test against production events.db (no writes).
    import json, hashlib
    DB = r"C:\Users\sirok\MoCKA\data\mocka_events.db"

    def sha(p):
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for c in iter(lambda: f.read(1 << 20), b""):
                h.update(c)
        return h.hexdigest()

    con = open_events_readonly(DB)
    write_rejected = False
    try:
        con.execute("CREATE TABLE _rl_should_fail (x int)")
    except sqlite3.OperationalError:
        write_rejected = True
    rows = load_rows(con)
    queries = ["reverse traceability improvement candidate",
               "reverse traceability",
               "provenance relay operator origin"]
    cmps = [compare(rows, q) for q in queries]
    # traversal demo on first v2 hit
    seed_id = next((c["v2_ids"][0] for c in cmps if c["v2_ids"]), None)
    trav = None
    if seed_id:
        by_id = {r["event_id"]: r for r in rows}
        seed_row = by_id.get(seed_id)
        trav = relationship_traversal(seed_row, lambda i: by_id.get(i), hops=1)
    con.close()
    print(json.dumps({"write_rejected": write_rejected,
                      "comparisons": cmps,
                      "traversal_1hop": trav}, ensure_ascii=False, indent=2))
