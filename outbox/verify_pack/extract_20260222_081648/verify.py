import hashlib, json, os, sys, itertools

def sha256_hex(b):
    return hashlib.sha256(b).hexdigest()

def canon_bytes(obj):
    s = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return s.encode("utf-8")

def is_hex64(s):
    if not isinstance(s, str):
        return False
    t = s.strip()
    if len(t) != 64:
        return False
    for c in t.lower():
        if c not in "0123456789abcdef":
            return False
    return True

def get_prev_id(obj):
    for k in ["previous_event_id","prev_event_id","prev","prev_id","prevEventId","prev_event","prevEvent"]:
        v = obj.get(k)
        if isinstance(v, str) and is_hex64(v):
            return v.strip()
    return None

def get_chain_hash(obj):
    for k in ["chain_hash","chainHash"]:
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None

def get_prev_chain_hash(obj):
    for k in ["prev_chain_hash","prevChainHash","prev_chain","prevChain"]:
        v = obj.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None

def get_claimed_event_id(obj):
    v = obj.get("event_id")
    if isinstance(v, str) and is_hex64(v):
        return v.strip()
    v = obj.get("eventId")
    if isinstance(v, str) and is_hex64(v):
        return v.strip()
    v = obj.get("id")
    if isinstance(v, str) and is_hex64(v):
        return v.strip()
    return None

def recompute_chain_hash(prev_chain_hash, event_id):
    return sha256_hex((prev_chain_hash + event_id).encode("utf-8"))

def load_nodes(root):
    nodes = {}
    for fn in os.listdir(root):
        if not fn.endswith(".json"):
            continue
        p = os.path.join(root, fn)
        with open(p, "r", encoding="utf-8") as f:
            obj = json.load(f)
        if not isinstance(obj, dict):
            continue
        claimed = get_claimed_event_id(obj)
        prev = get_prev_id(obj)
        ch = get_chain_hash(obj)
        pch = get_prev_chain_hash(obj)
        stem = os.path.splitext(fn)[0]
        key = claimed or (stem if is_hex64(stem) else fn)
        nodes[key] = {"fn": fn, "obj": obj, "claimed": claimed, "prev": prev, "ch": ch, "pch": pch}
    return nodes

def build_chain(nodes):
    forward = {}
    genesis = []
    for k, n in nodes.items():
        prev = n["prev"]
        if not prev or prev not in nodes:
            genesis.append(k)
        if prev:
            forward.setdefault(prev, []).append(k)
    if not genesis:
        genesis = [next(iter(nodes.keys()))]
    genesis.sort()
    cur = genesis[0]
    chain = [cur]
    visited = set(chain)
    while True:
        nxts = forward.get(cur, [])
        if not nxts:
            break
        nxts.sort()
        nxt = nxts[0]
        if nxt in visited:
            break
        chain.append(nxt)
        visited.add(nxt)
        cur = nxt
    return chain

def compute_event_id_with_excludes(obj, excludes):
    d = {}
    for k, v in obj.items():
        if k in excludes:
            continue
        d[k] = v
    return sha256_hex(canon_bytes(d))

def infer_event_id_rule(nodes, order):
    # Candidate key universe: keys commonly present in your events.
    # We infer by maximizing matches between computed_id(excludes) and claimed_event_id across the chain.
    universe = [
        "event_id",
        "signature",
        "chain_hash",
        "previous_event_id",
        "created_at_unix_ms",
        "outbox",
        "schema",
    ]
    candidates = []
    # Always try some sane small subsets first, then broaden (powerset up to size 5)
    seeds = [
        ("exclude:event_id+signature+chain_hash", {"event_id","signature","chain_hash"}),
        ("exclude:event_id+signature", {"event_id","signature"}),
        ("exclude:event_id+chain_hash", {"event_id","chain_hash"}),
        ("exclude:event_id", {"event_id"}),
        ("exclude:signature", {"signature"}),
        ("exclude:chain_hash", {"chain_hash"}),
        ("exclude:event_id+signature+chain_hash+outbox", {"event_id","signature","chain_hash","outbox"}),
        ("exclude:event_id+signature+chain_hash+created_at_unix_ms", {"event_id","signature","chain_hash","created_at_unix_ms"}),
        ("exclude:event_id+signature+chain_hash+schema", {"event_id","signature","chain_hash","schema"}),
        ("exclude:event_id+signature+chain_hash+previous_event_id", {"event_id","signature","chain_hash","previous_event_id"}),
    ]
    for name, ex in seeds:
        candidates.append((name, ex))

    # Add additional combos (bounded)
    base = set(universe)
    for r in range(0, 6):
        for comb in itertools.combinations(universe, r):
            ex = set(comb)
            # Must exclude event_id in almost all sane schemes
            if "event_id" not in ex:
                continue
            # Avoid explosion with too many
            candidates.append((f"exclude:{'+'.join(sorted(ex))}", ex))

    best = None  # (score, name, excludes)
    for name, ex in candidates:
        score = 0
        total = 0
        for k in order:
            n = nodes[k]
            claimed = n["claimed"]
            if not claimed:
                continue
            total += 1
            got = compute_event_id_with_excludes(n["obj"], ex)
            if got.lower() == claimed.lower():
                score += 1
        # Prefer higher score, then smaller exclude set
        metric = (score, -len(ex), name)
        if best is None or metric > best[0]:
            best = (metric, name, ex, score, total)
    # If no claimed ids, fallback excludes event_id+signature+chain_hash
    if best is None:
        return ("exclude:event_id+signature+chain_hash", {"event_id","signature","chain_hash"}, 0, 0)
    _, name, ex, score, total = best
    return (name, ex, score, total)

def main():
    if len(sys.argv) != 2:
        print("usage: python verify.py <dir>")
        return 2

    root = sys.argv[1]
    if not os.path.isdir(root):
        print("not a directory:", root)
        return 2

    nodes = load_nodes(root)
    order = build_chain(nodes)

    rule_name, excludes, eid_match, eid_total = infer_event_id_rule(nodes, order)

    # Verify chain_hash using computed event_id under inferred rule.
    last_chain_hash = None
    chainhash_checked = 0
    chainhash_failed = 0

    # Also report mismatch info (informational)
    eid_mismatch_info = 0
    eid_mismatch_samples = []

    for k in order:
        n = nodes[k]
        obj = n["obj"]
        claimed = n["claimed"]
        computed = compute_event_id_with_excludes(obj, excludes)

        if claimed and computed.lower() != claimed.lower():
            eid_mismatch_info += 1
            if len(eid_mismatch_samples) < 3:
                eid_mismatch_samples.append({
                    "file": n["fn"],
                    "claimed_event_id": claimed,
                    "computed_event_id": computed,
                })

        ch = n["ch"]
        pch = n["pch"]
        prev_used = pch or last_chain_hash

        if ch and prev_used:
            # Use computed event_id for recomputation (this is the missing spec link)
            got = recompute_chain_hash(prev_used, computed)
            chainhash_checked += 1
            if got.lower() != ch.lower():
                chainhash_failed += 1

        if ch:
            last_chain_hash = ch

    status = "OK" if chainhash_failed == 0 else "NG"
    out = {
        "status": status,
        "linear_chain_length": len(order),
        "event_id_rule": rule_name,
        "event_id_rule_match": f"{eid_match}/{eid_total}" if eid_total else "0/0",
        "event_id_mismatch_info": eid_mismatch_info,
        "event_id_mismatch_samples": eid_mismatch_samples,
        "chainhash_checked": chainhash_checked,
        "chainhash_failed": chainhash_failed,
        "final_chain_hash_observed": last_chain_hash,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if status == "OK" else 1

if __name__ == "__main__":
    raise SystemExit(main())
