# W-2 read layer: Decision Ledger reverse-traceability resolver (derived, read-only).
# DC_20260714_001. Non-destructive: reads decision_ledger.jsonl read-only, derives
# superseded_by / is_superseded at read time. Never writes the ledger, never changes
# status, never backfills superseded_by, never touches DC_20260712_008.
import json

DEFAULT_LEDGER = r"C:\Users\sirok\MoCKA\data\decisions\decision_ledger.jsonl"


def load_ledger(path=DEFAULT_LEDGER):
    """Read-only load. Append-only latest-wins per decision_id. Broken lines counted."""
    latest, order, broken = {}, [], 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except Exception:
                broken += 1
                continue
            did = r.get("decision_id")
            if did not in latest:
                order.append(did)
            latest[did] = r
    return latest, order, broken


def build_reverse(latest):
    """From forward `supersedes`, derive reverse links. Self-references are isolated
    (never create a self-loop; reported separately)."""
    reverse = {}      # target_id -> superseding_id
    self_refs = []
    for did, r in latest.items():
        sup = r.get("supersedes")
        if not sup:
            continue
        if sup == did:
            self_refs.append(did)   # anomaly retained, not corrected (D-6)
            continue
        reverse[sup] = did
    return reverse, self_refs


def resolve(path=DEFAULT_LEDGER):
    """Return a derived view: each decision with computed superseded_by / is_superseded.
    The underlying ledger is not modified. `stored_*` shows the actual file values."""
    latest, order, broken = load_ledger(path)
    reverse, self_refs = build_reverse(latest)
    view = []
    for did in order:
        r = latest[did]
        superseded_by = reverse.get(did)
        view.append({
            "decision_id": did,
            "status": r.get("status"),                 # unchanged (derived layer never edits)
            "supersedes": r.get("supersedes"),
            "is_superseded": superseded_by is not None,   # DERIVED
            "superseded_by": superseded_by,               # DERIVED (None if not superseded)
            "stored_superseded_by": r.get("superseded_by"),  # actual file value (kept as-is)
            "self_supersession": did in self_refs,
        })
    return {"view": view, "reverse_map": reverse, "self_refs": self_refs,
            "broken_lines": broken, "count": len(order)}


if __name__ == "__main__":
    import hashlib
    LEDGER = DEFAULT_LEDGER

    def sha(p):
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for c in iter(lambda: f.read(1 << 20), b""):
                h.update(c)
        return h.hexdigest()

    h1 = sha(LEDGER)
    res = resolve(LEDGER)
    h2 = sha(LEDGER)
    superseded = [v["decision_id"] for v in res["view"] if v["is_superseded"]]
    stored_nonnull = [v["decision_id"] for v in res["view"]
                      if v["stored_superseded_by"] not in (None, "")]
    print(json.dumps({
        "count": res["count"],
        "reverse_map": res["reverse_map"],
        "derived_superseded_ids": superseded,
        "self_refs": res["self_refs"],
        "stored_superseded_by_nonnull": stored_nonnull,  # expected [] (ledger unchanged)
        "ledger_sha256_before": h1,
        "ledger_sha256_after": h2,
        "ledger_unchanged": h1 == h2,
    }, ensure_ascii=False, indent=2))
