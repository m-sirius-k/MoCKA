import hashlib, json, os, sys

def sha256_hex(b):
    return hashlib.sha256(b).hexdigest()

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

def get_event_id(obj):
    for k in ["event_id","eventId","id"]:
        v = obj.get(k)
        if isinstance(v, str) and is_hex64(v):
            return v.strip()
    return None

def get_prev_id(obj):
    for k in ["previous_event_id","prev_event_id","previousEventId","prevEventId","prev","prev_id","prev_event","prevEvent"]:
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
        eid = get_event_id(obj)
        if not eid:
            continue
        nodes[eid] = {"fn": fn, "obj": obj}
    return nodes

def build_chain(nodes):
    forward = {}
    genesis = []
    for eid, n in nodes.items():
        prev = get_prev_id(n["obj"])
        if not prev or prev not in nodes:
            genesis.append(eid)
        if prev:
            forward.setdefault(prev, []).append(eid)

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

def verify_chain_hash(chain, nodes):
    # Rules accepted (compat):
    # A) atomic_append: if no prev -> chain_hash == event_id
    # B) atomic_append / contract_v1: sha256(prev_event_id + event_id)
    # C) audit_writer: sha256(prev_chain_hash + event_id)
    # D) audit_writer fallback: sha256((prev_event_id or "GENESIS") + event_id)
    failed = 0
    matched = {"A_genesis_eq_eid":0, "B_prev_eid_plus_eid":0, "C_prev_chain_plus_eid":0, "D_genesis_or_prev_eid_plus_eid":0}

    prev_eid = None
    prev_chain_hash = None

    for eid in chain:
        obj = nodes[eid]["obj"]
        stored = get_chain_hash(obj) or ""
        prev_ptr = get_prev_id(obj)  # may be None at genesis

        candidates = []

        # A) genesis special
        if not prev_ptr:
            candidates.append(("A_genesis_eq_eid", eid))
            candidates.append(("D_genesis_or_prev_eid_plus_eid", sha256_hex(("GENESIS" + eid).encode("utf-8"))))
        else:
            # B) prev_event_id + eid
            candidates.append(("B_prev_eid_plus_eid", sha256_hex((prev_ptr + eid).encode("utf-8"))))

            # C) prev_chain_hash + eid (if we have it)
            if prev_chain_hash:
                candidates.append(("C_prev_chain_plus_eid", sha256_hex((prev_chain_hash + eid).encode("utf-8"))))

            # D) (prev_event_id or GENESIS) + eid
            base = (prev_ptr or "GENESIS") + eid
            candidates.append(("D_genesis_or_prev_eid_plus_eid", sha256_hex(base.encode("utf-8"))))

        ok = False
        for name, cand in candidates:
            if cand.lower() == stored.lower():
                matched[name] += 1
                ok = True
                break

        if not ok:
            failed += 1

        prev_eid = eid
        prev_chain_hash = stored or prev_chain_hash

    return failed, matched

def main():
    if len(sys.argv) != 2:
        print("usage: python verify.py <dir>")
        return 2

    root = sys.argv[1]
    if not os.path.isdir(root):
        print("not a directory:", root)
        return 2

    nodes = load_nodes(root)
    chain = build_chain(nodes)

    failed, matched = verify_chain_hash(chain, nodes)

    status = "OK" if failed == 0 else "NG"
    out = {
        "status": status,
        "linear_chain_length": len(chain),
        "chainhash_failed": failed,
        "chainhash_matched_counts": matched,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if status == "OK" else 1

if __name__ == "__main__":
    raise SystemExit(main())
